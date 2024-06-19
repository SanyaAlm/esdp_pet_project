const shopData = new URLSearchParams(window.location.search)
console.log(shopData)
let productData = shopData.get('products')
console.log(productData)

const parsedShopData = JSON.parse(productData);
console.log('parsedShopData', parsedShopData)

const shopDataContainer = document.getElementById('shopDataContainer')

parsedShopData.forEach(product => {
  product.images.forEach(imageObj => {
    shopDataContainer.innerHTML += `
      <div id="carouselExampleControls" class="carousel slide" data-bs-ride="carousel">
        <div class="carousel-inner">
          <div class="carousel-item active">
            <img src='${imageObj.image}' class="d-block w-100" alt="...">
          </div>
        </div>
        <button class="carousel-control-prev" type="button" data-bs-target="#carouselExampleControls" data-bs-slide="prev">
          <span class="carousel-control-prev-icon" aria-hidden="true"></span>
          <span class="visually-hidden">Previous</span>
        </button>
        <button class="carousel-control-next" type="button" data-bs-target="#carouselExampleControls" data-bs-slide="next">
          <span class="carousel-control-next-icon" aria-hidden="true"></span>
          <span class="visually-hidden">Next</span>
        </button>
      </div>
      <div class="card-body text-center">
        <h5 class="card-title">${product.name}</h5>
        <p class="card-text text-center">Цена: ${product.price}</p>
        <p class="card-text text-center">${product.description}</p>
        <a href="#" class="btn btn-primary text-center">Заказать</a>
      </div>
    `;
  });
});