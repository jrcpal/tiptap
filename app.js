async function returnBeer(evt) {
    evt.preventDefault()

    const response = await fetch("https://sandbox-api.brewerydb.com/v2/beer/random?key=00e5f08fc31d4f272660c804487c1b7c",
    {mode: 'no-cors',
    method: 'GET',}
    ); // Generate the Response object
    if (response.ok) {
    const jsonValue = await response.json(); // Get JSON value from the response body
    handleResponse(Promise.resolve(jsonValue));
  } else {
    return Promise.reject('*** 404: Not found');
  }
}

function handleResponse(jsonValue) {
  // Post response data into beer-results div
  $('#beer-results').html(`
  <p>Your beer is ${jsonValue}</p>`)
  console.log(jsonValue)
}



// $("#beer-form").on("submit", returnBeer);


async function rateBeer(recipient_beer) {

  //grab all info from rated beer modal
  const data_obj = JSON.stringify(recipient_beer)

  const res = await axios.post('/rate-beer', data_obj, {
      headers: {
          'Content-Type': 'application/json'
      }
  })
  console.log("async function ran")
  return res
}


// $("#beer-form").on("submit", saveBeer);


$('#rate-modal').on('show.bs.modal', function (event) {
  let button = $(event.relatedTarget) // Button that triggered the modal
  let recipient = button.data('name') // Extract info from data-* attributes
  let recipient_beer = button.data('beer')
  let modal = $(this)
  modal.find('.modal-title').text('Rate' + recipient)
  modal.find('.modal-body .hidden input').val(recipient_beer)
})


// $('.submit-rating').click(deleteBeerFromSaved)



// async function deleteBeerFromSaved() {
//     const id = $(this).data('id')
//     await axios.delete(`beer/${id}`)
//     $(this).parent().remove()
// }

