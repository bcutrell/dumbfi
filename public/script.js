// TODO: DOMPurify
GridStack.renderCB = function (el, w) {
  el.innerHTML = w.content;
};

let children = [
  {
    x: 0,
    y: 0,
    w: 4,
    h: 2,
    content:
    '<div class="ht-100-pct nes-container with-title is-centered"><p class="title">1</p><p>1</p></div>',
  },
  {
    x: 4,
    y: 0,
    w: 4,
    h: 4,
    content:
    '<div class="ht-100-pct nes-container with-title is-centered"><p class="title">2</p><p>2</p></div>',
  },
  {
    x: 8,
    y: 0,
    w: 2,
    h: 2,
    content:
    '<div class="ht-100-pct nes-container with-title is-centered"><p class="title">3</p><p>3</p></div>',
  },
  {
    x: 10,
    y: 0,
    w: 2,
    h: 2,
    content:
    '<div class="ht-100-pct nes-container with-title is-centered"><p class="title">4</p><p>4</p></div>',
  },
  {
    x: 0,
    y: 2,
    w: 2,
    h: 2,
    content:
    '<div class="ht-100-pct nes-container with-title is-centered"><p class="title">5</p><p>5</p></div>',
  },
  {
    x: 2,
    y: 2,
    w: 2,
    h: 4,
    content:
    '<div class="ht-100-pct nes-container with-title is-centered"><p class="title">6</p><p>6</p></div>',
  },
  {
    x: 8,
    y: 2,
    w: 4,
    h: 2,
    content:
    '<div class="ht-100-pct nes-container with-title is-centered"><p class="title">7</p><p>7</p></div>',
  },
  {
    x: 0,
    y: 4,
    w: 2,
    h: 2,
    content:
    '<div class="ht-100-pct nes-container with-title is-centered"><p class="title">8</p><p>8</p></div>',
  },
  {
    x: 4,
    y: 4,
    w: 4,
    h: 2,
    content:
    '<div class="ht-100-pct nes-container with-title is-centered"><p class="title">9</p><p>9</p></div>',
  },
  {
    x: 8,
    y: 4,
    w: 2,
    h: 2,
    content:
    '<div class="ht-100-pct nes-container with-title is-centered"><p class="title">10</p><div id="chart"></div></div>',
  },
  {
    x: 10,
    y: 4,
    w: 2,
    h: 2,
    content:
    '<div class="ht-100-pct nes-container with-title is-centered"><p class="title">11</p><p>11</p></div>',
  },
];

let grid = GridStack.init({ cellHeight: 70, children });
grid.on("added removed change", function (e, items) {
  let str = "";
  items.forEach(function (item) {
    str += " (x,y)=" + item.x + "," + item.y;
  });
  console.log(e.type + " " + items.length + " items:" + str);
});

// Sample data
const data = [
  { name: "A", value: 20 },
  { name: "B", value: 35 },
  { name: "C", value: 15 },
  { name: "D", value: 40 },
  { name: "E", value: 25 }
];

// Select the parent div
const container = d3.select("#chart"); // Replace #chart-container with the actual ID

// Create SVG element within the container
const svg = container.append("svg");

// Function to draw or redraw the chart
function drawChart() {
  // Get the current width and height of the container
  const width = container.node().clientWidth;
  const height = container.node().clientHeight;
  
  // Set SVG dimensions based on container size
  svg.attr("width", width).attr("height", height);
  
  // Scales
  const xScale = d3.scaleBand()
  .domain(data.map(d => d.name))
  .range([0, width])
  .padding(0.1);
  
  const yScale = d3.scaleLinear()
  .domain([0, d3.max(data, d => d.value)])
  .range([height, 0]);
  
  // Bars
  svg.selectAll(".bar")
  .data(data)
  .join(
    enter => enter.append("rect")
    .attr("class", "bar")
    .attr("fill", "steelblue"),
    update => update,
    exit => exit.remove()
  )
  .attr("x", d => xScale(d.name))
  .attr("y", d => yScale(d.value))
  .attr("width", xScale.bandwidth())
  .attr("height", d => height - yScale(d.value));
  
  
  // Axes (example - you can customize these)
  svg.selectAll(".axis").remove(); // Clear previous axes
  svg.append("g")
  .attr("class", "axis")
  .attr("transform", `translate(0, ${height})`)
  .call(d3.axisBottom(xScale));
  
  svg.append("g")
  .attr("class", "axis")
  .call(d3.axisLeft(yScale));
}

// Initial draw
drawChart();

const resizeObserver = new ResizeObserver(entries => {
  for (let entry of entries) {
    if (entry.target === container.node()) {
      drawChart();
    }
  }
});

resizeObserver.observe(container.node());