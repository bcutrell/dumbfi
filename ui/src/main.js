import * as d3 from "d3";

const data = [
  {
    date: "2024-01-01",
    AAPL: 47,
    IBM: 25,
    MSFT: 28,
  },
  {
    date: "2024-01-02",
    AAPL: 39,
    IBM: 16,
    MSFT: 45,
  },
  {
    date: "2024-01-03",
    AAPL: 54,
    IBM: 26,
    MSFT: 20,
  },
];

// Chart dimensions
const width = 800;
const height = 400;
const margin = { top: 20, right: 30, left: 40, bottom: 40 };

// Create SVG
const svg = d3
  .select("#app")
  .append("svg")
  .attr("width", width)
  .attr("height", height);

// Setup scales
const x = d3
  .scaleBand()
  .domain(data.map((d) => d.date))
  .range([margin.left, width - margin.right])
  .padding(0.0);

const y = d3
  .scaleLinear()
  .domain([0, 100])
  .range([height - margin.bottom, margin.top]);

// Stack the data
const series = d3.stack().keys(["AAPL", "IBM", "MSFT"])(data);

// Color scale
const color = d3
  .scaleOrdinal()
  .domain(["AAPL", "IBM", "MSFT"])
  .range(["#8884d8", "#82ca9d", "#ffc658"]);

// Add bars
svg
  .append("g")
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
  .attr("width", x.bandwidth());

// Add axes
svg
  .append("g")
  .attr("transform", `translate(0,${height - margin.bottom})`)
  .call(d3.axisBottom(x));

svg
  .append("g")
  .attr("transform", `translate(${margin.left},0)`)
  .call(d3.axisLeft(y).ticks(null, "s"));
