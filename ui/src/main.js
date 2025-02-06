import * as d3 from "d3";

function generateWeightData(
  numDays = 100,
  tickers = ["AAPL", "IBM", "MSFT"],
  startPrice = 100,
  volatility = 0.02,
  drift = 0.0005,
) {
  const data = [];
  const prices = {};

  tickers.forEach((ticker) => {
    prices[ticker] = startPrice;
  });

  for (let i = 0; i < numDays; i++) {
    const date = new Date(2024, 0, 1 + i); //  Date object
    const entry = { date };

    tickers.forEach((ticker) => {
      const dailyReturn = drift + volatility * (Math.random() * 2 - 1);
      prices[ticker] *= Math.exp(dailyReturn);
    });

    const totalValue = Object.values(prices).reduce((sum, p) => sum + p, 0);
    tickers.forEach((ticker) => {
      entry[ticker] = parseFloat(
        ((prices[ticker] / totalValue) * 100).toFixed(2),
      );
    });

    data.push(entry);
  }

  return data;
}

function createStackedBarChart(data, tickers, containerId) {
  const width = 800;
  const height = 400;
  const margin = { top: 20, right: 30, left: 60, bottom: 40 }; // Increased left margin

  const svg = d3
    .select(containerId)
    .append("svg")
    .attr("width", width)
    .attr("height", height);

  const x = d3
    .scaleTime() // Use scaleTime for dates
    .domain(d3.extent(data, (d) => d.date))
    .range([margin.left, width - margin.right]);

  const y = d3
    .scaleLinear()
    .domain([0, 100])
    .range([height - margin.bottom, margin.top]);

  const series = d3.stack().keys(tickers)(data);

  const color = d3
    .scaleOrdinal()
    .domain(tickers)
    .range(["#8884d8", "#82ca9d", "#ffc658"]);

  const chartGroup = svg.append("g");

  chartGroup
    .selectAll("g")
    .data(series)
    .join("g")
    .attr("fill", (d) => color(d.key))
    .selectAll("rect")
    .data((d) => d)
    .join("rect")
    .attr("x", (d) => x(d.data.date))
    .attr("y", (d) => y(d[1]))
    .attr("height", (d) => y(d[0]) - y(d[1]))
    .attr("width", (d) => {
      //calculate the width of one bar by subtracting the x position of the next bar from the x position of the current bar
      const nextDataPoint = data[data.indexOf(d.data) + 1];
      if (nextDataPoint) {
        return x(nextDataPoint.date) - x(d.data.date);
      } else {
        // For the last bar, estimate width based on the previous difference or a minimum value
        const prevDataPoint = data[data.indexOf(d.data) - 1];
        return prevDataPoint ? x(d.data.date) - x(prevDataPoint.date) : 5; // Use a default width if no previous point
      }
    });

  const xAxis = d3.axisBottom(x).tickFormat(d3.timeFormat("%b %d")); // Format the date
  const yAxis = d3.axisLeft(y).ticks(null, "s");

  const xAxisGroup = svg
    .append("g")
    .attr("transform", `translate(0,${height - margin.bottom})`)
    .call(xAxis);

  svg.append("g").attr("transform", `translate(${margin.left},0)`).call(yAxis);

  // Rotate x-axis labels
  xAxisGroup
    .selectAll("text")
    .style("text-anchor", "end")
    .attr("dx", "-.8em")
    .attr("dy", ".15em")
    .attr("transform", "rotate(-45)");

  // Mouseover lines (interaction)
  const verticalLine = svg
    .append("line")
    .attr("stroke", "black")
    .attr("stroke-width", 1)
    .style("opacity", 0);

  const horizontalLine = svg
    .append("line")
    .attr("stroke", "black")
    .attr("stroke-width", 1)
    .style("opacity", 0);

  svg
    .on("mousemove", function (event) {
      const [mouseX, mouseY] = d3.pointer(event);

      if (
        mouseX >= margin.left &&
        mouseX <= width - margin.right &&
        mouseY >= margin.top &&
        mouseY <= height - margin.bottom
      ) {
        verticalLine
          .attr("x1", mouseX)
          .attr("y1", margin.top)
          .attr("x2", mouseX)
          .attr("y2", height - margin.bottom)
          .style("opacity", 1);

        horizontalLine
          .attr("x1", margin.left)
          .attr("y1", mouseY)
          .attr("x2", width - margin.right)
          .attr("y2", mouseY)
          .style("opacity", 1);
      } else {
        verticalLine.style("opacity", 0);
        horizontalLine.style("opacity", 0);
      }
    })
    .on("mouseleave", function () {
      verticalLine.style("opacity", 0);
      horizontalLine.style("opacity", 0);
    });

  // Brush and Zoom
  const brush = d3
    .brushX()
    .extent([
      [margin.left, 0],
      [width - margin.right, height - margin.bottom],
    ])
    .on("end", brushed);

  const zoom = d3
    .zoom()
    .scaleExtent([1, 32]) //  zoom scale
    .translateExtent([
      [margin.left, 0],
      [width - margin.right, height - margin.bottom],
    ])
    .extent([
      [margin.left, 0],
      [width - margin.right, height - margin.bottom],
    ])
    .on("zoom", zoomed);

  //  clip path to prevent bars from going outside the chart area during zoom
  svg
    .append("defs")
    .append("clipPath")
    .attr("id", "clip")
    .append("rect")
    .attr("x", margin.left)
    .attr("y", margin.top)
    .attr("width", width - margin.left - margin.right)
    .attr("height", height - margin.top - margin.bottom);

  chartGroup.attr("clip-path", "url(#clip)");

  const brushGroup = svg.append("g").attr("class", "brush").call(brush);

  function brushed(event) {
    const selection = event.selection;
    if (selection) {
      const [x0, x1] = selection.map(x.invert); // Convert pixel to dates
      const newXDomain = [x0, x1];
      x.domain(newXDomain);
      svg.select(".brush").call(brush.move, null); // Remove brush after zoom

      //recalculate bar width inside brushed function
      chartGroup
        .selectAll("rect")
        .attr("x", (d) => x(d.data.date))
        .attr("width", (d) => {
          const nextDataPoint = data[data.indexOf(d.data) + 1];
          if (nextDataPoint && x(nextDataPoint.date)) {
            return x(nextDataPoint.date) - x(d.data.date);
          } else {
            // For the last bar, estimate width
            const prevDataPoint = data[data.indexOf(d.data) - 1];
            return prevDataPoint && x(d.data.date)
              ? x(d.data.date) - x(prevDataPoint.date)
              : 5; // Use a default
          }
        });

      svg.select(".brush").call(brush.move, null); // Clear the brush
      svg.call(
        zoom.transform,
        d3.zoomIdentity
          .scale(width / (x.range()[1] - x.range()[0]))
          .translate(-x.range()[0], 0),
      );
    }
  }

  function zoomed(event) {
    if (event.sourceEvent && event.sourceEvent.type === "brush") return; // Ignore zoom triggered by brush
    const newXScale = event.transform.rescaleX(x); // Use the original x scale for date info
    x.domain(newXScale.domain()); // Update the x-domain

    //recalculate bar width inside zoom function
    chartGroup
      .selectAll("rect")
      .attr("x", (d) => x(d.data.date))
      .attr("width", (d) => {
        const nextDataPoint = data[data.indexOf(d.data) + 1];
        if (nextDataPoint && x(nextDataPoint.date)) {
          return x(nextDataPoint.date) - x(d.data.date);
        } else {
          // For the last bar, estimate width
          const prevDataPoint = data[data.indexOf(d.data) - 1];
          return prevDataPoint && x(d.data.date)
            ? x(d.data.date) - x(prevDataPoint.date)
            : 5;
        }
      });

    xAxisGroup.call(xAxis.scale(newXScale)); // Update axis

    //re-rotate labels
    xAxisGroup
      .selectAll("text")
      .style("text-anchor", "end")
      .attr("dx", "-.8em")
      .attr("dy", ".15em")
      .attr("transform", "rotate(-45)");
  }
}

const data = generateWeightData(500, ["AAPL", "IBM", "MSFT"]);
createStackedBarChart(data, ["AAPL", "IBM", "MSFT"], "#app");
