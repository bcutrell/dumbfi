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
          '<div class="ht-100-pct nes-container with-title is-centered"><p class="title">10</p><p>10</p></div>',
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