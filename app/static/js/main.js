
(function ($) {
    "use strict";

    /*[ Load page ]
    ===========================================================*/
    $(".animsition").animsition({
        inClass: 'fade-in',
        outClass: 'fade-out',
        inDuration: 1500,
        outDuration: 800,
        linkElement: '.animsition-link',
        loading: true,
        loadingParentElement: 'html',
        loadingClass: 'animsition-loading-1',
        loadingInner: '<div class="loader05"></div>',
        timeout: false,
        timeoutCountdown: 5000,
        onLoadEvent: true,
        browser: [ 'animation-duration', '-webkit-animation-duration'],
        overlay : false,
        overlayClass : 'animsition-overlay-slide',
        overlayParentElement : 'html',
        transition: function(url){ window.location.href = url; }
    });
    
    /*[ Back to top ]
    ===========================================================*/
    var windowH = $(window).height()/2;

    $(window).on('scroll',function(){
        if ($(this).scrollTop() > windowH) {
            $("#myBtn").css('display','flex');
        } else {
            $("#myBtn").css('display','none');
        }
    });

    $('#myBtn').on("click", function(){
        $('html, body').animate({scrollTop: 0}, 300);
    });


    /*==================================================================
    [ Fixed Header ]*/
    var headerDesktop = $('.container-menu-desktop');
    var wrapMenu = $('.wrap-menu-desktop');

    if($('.top-bar').length > 0) {
        var posWrapHeader = $('.top-bar').height();
    }
    else {
        var posWrapHeader = 0;
    }
    

    if($(window).scrollTop() > posWrapHeader) {
        $(headerDesktop).addClass('fix-menu-desktop');
        $(wrapMenu).css('top',0); 
    }  
    else {
        $(headerDesktop).removeClass('fix-menu-desktop');
        $(wrapMenu).css('top',posWrapHeader - $(this).scrollTop()); 
    }

    $(window).on('scroll',function(){
        if($(this).scrollTop() > posWrapHeader) {
            $(headerDesktop).addClass('fix-menu-desktop');
            $(wrapMenu).css('top',0); 
        }  
        else {
            $(headerDesktop).removeClass('fix-menu-desktop');
            $(wrapMenu).css('top',posWrapHeader - $(this).scrollTop()); 
        } 
    });


    /*==================================================================
    [ Menu mobile ]*/
    $('.btn-show-menu-mobile').on('click', function(){
        $(this).toggleClass('is-active');
        $('.menu-mobile').slideToggle();
    });

    var arrowMainMenu = $('.arrow-main-menu-m');

    for(var i=0; i<arrowMainMenu.length; i++){
        $(arrowMainMenu[i]).on('click', function(){
            $(this).parent().find('.sub-menu-m').slideToggle();
            $(this).toggleClass('turn-arrow-main-menu-m');
        })
    }

    $(window).resize(function(){
        if($(window).width() >= 992){
            if($('.menu-mobile').css('display') == 'block') {
                $('.menu-mobile').css('display','none');
                $('.btn-show-menu-mobile').toggleClass('is-active');
            }

            $('.sub-menu-m').each(function(){
                if($(this).css('display') == 'block') { console.log('hello');
                    $(this).css('display','none');
                    $(arrowMainMenu).removeClass('turn-arrow-main-menu-m');
                }
            });
                
        }
    });


    /*==================================================================
    [ Show / hide modal search ]*/
    $('.js-show-modal-search').on('click', function(){
        $('.modal-search-header').addClass('show-modal-search');
        $(this).css('opacity','0');
    });

    $('.js-hide-modal-search').on('click', function(){
        $('.modal-search-header').removeClass('show-modal-search');
        $('.js-show-modal-search').css('opacity','1');
    });

    $('.container-search-header').on('click', function(e){
        e.stopPropagation();
    });


    /*==================================================================
    [ Isotope ]*/
    var $topeContainer = $('.isotope-grid');
    var $filter = $('.filter-tope-group');

    // filter items on button click
    $filter.each(function () {
        $filter.on('click', 'button', function () {
            var filterValue = $(this).attr('data-filter');
            $topeContainer.isotope({filter: filterValue});
        });
        
    });

    // init Isotope
    $(window).on('load', function () {
        var $grid = $topeContainer.each(function () {
            $(this).isotope({
                itemSelector: '.isotope-item',
                layoutMode: 'fitRows',
                percentPosition: true,
                animationEngine : 'best-available',
                masonry: {
                    columnWidth: '.isotope-item'
                }
            });
        });
    });

    var isotopeButton = $('.filter-tope-group button');

    $(isotopeButton).each(function(){
        $(this).on('click', function(){
            for(var i=0; i<isotopeButton.length; i++) {
                $(isotopeButton[i]).removeClass('how-active1');
            }

            $(this).addClass('how-active1');
        });
    });

    /*==================================================================
    [ Filter / Search product ]*/
    $('.js-show-filter').on('click',function(){
        $(this).toggleClass('show-filter');
        $('.panel-filter').slideToggle(400);

        if($('.js-show-search').hasClass('show-search')) {
            $('.js-show-search').removeClass('show-search');
            $('.panel-search').slideUp(400);
        }    
    });

    $('.js-show-search').on('click',function(){
        $(this).toggleClass('show-search');
        $('.panel-search').slideToggle(400);

        if($('.js-show-filter').hasClass('show-filter')) {
            $('.js-show-filter').removeClass('show-filter');
            $('.panel-filter').slideUp(400);
        }    
    });




    /*==================================================================
    [ Cart ]*/
     // Show cart when .js-show-cart is clicked
     $('.js-show-cart').on('click', function() {
        $.ajax({
            url: '/cart', // Make sure this matches your Express route
            method: 'GET',
            success: function(data) {
                // Inject the fetched HTML into the panel cart div
                $('.js-panel-cart').html(data);
                // Show the cart by adding the class
                $('.js-panel-cart').addClass('show-header-cart');
            },
            error: function(xhr) {
                console.error('Error loading cart:', xhr.responseText);
            }
        });
    });
    
    // Hide cart on click
  
    
    $(document).on('click', '.js-hide-cart', function() {
        // Try removing the `show-header-cart` class directly on click
        console.log("Closing cart...");
        $('.js-panel-cart').removeClass('show-header-cart');
    });

    // $('.js-show-cart').on('click',function(){
    //     $('.js-panel-cart').addClass('show-header-cart');
    // });

    // $('.js-hide-cart').on('click',function(){
    //     $('.js-panel-cart').removeClass('show-header-cart');
    // });

    /*==================================================================
    [ Cart ]*/

    


    $('.js-show-sidebar').on('click',function(){
        $('.js-sidebar').addClass('show-sidebar');
    });

    $('.js-hide-sidebar').on('click',function(){
        $('.js-sidebar').removeClass('show-sidebar');
    });

    // Mobile Sidebar

    $('.js-show-mobile-sidebar').on('click', function() {
        $.ajax({
            url: '/about-mobile', // Make sure this matches your Express route
            method: 'GET',
            success: function(data) {
                // Inject the fetched HTML into the panel cart div
                $('.js-panel-cart').html(data);
                // Show the cart by adding the class
                $('.js-panel-cart').addClass('show-header-cart');
            },
            error: function(xhr) {
                console.error('Error loading cart:', xhr.responseText);
            }
        });
    });
    
    // Hide cart on click
  
    
    $(document).on('click', '.js-hide-cart', function() {
        // Try removing the `show-header-cart` class directly on click
        console.log("Closing cart...");
        $('.js-panel-cart').removeClass('show-header-cart');
    });

   



    /*[ Cart Add to Cart Functionality ]*/
    $('.js-add-to-cart').on('click', function (e) {
        e.preventDefault();
    
        // Reference to the clicked button
        var $this = $(this);
    
        // Find the parent container for the product details
        var $productContainer = $this.closest('.product-details');
    
        // Find the parent container for the quantity input
        var $qtyContainer = $this.closest('.quantity-container');
    
        // Retrieve the product ID from the button's data attribute
        var productId = $this.data('product-id');
    
        // Retrieve the quantity, size, and color values
        var quantity = parseInt($productContainer.find('input[name="num-product"]').val()) || 1; // Ensure it matches the name attribute
        var size = $productContainer.find('select[name="size"]').val();
        var color = $productContainer.find('select[name="color"]').val();
    
        // Validate that size and color are selected
        // if (!size || !color) {
        //     alert('Please select both size and color before adding to cart.');
        //     return;
        // }
    
        // Prepare the data to be sent to the server
        var cartData = {
            productId: productId,
            quantity: quantity,
            size: size,
            color: color
        };
    
        console.log('Sending cart data:', cartData);
    
        // AJAX request to send the cart data to the server
        $.ajax({
            url: '/addCart', // Update this URL if needed
            method: 'POST',
            contentType: 'application/json',
            data: JSON.stringify(cartData),
            success: function (response) {
                console.log('Success response:', response);
                alert('Item successfully added to cart!');
                
                // Optionally, show or hide any UI elements (like a cart modal)
                $('.js-hide-modal1').click(); // Hides a modal, if used
                $('.js-show-cart').click();  // Shows the cart panel, if used
            },
            error: function (xhr) {
                console.error('Error adding item to cart:', xhr.responseText);
                alert('Failed to add item to cart. Please try again.');
            }
        });
    });


    $('.js-update-cart').on('click', function (e) {
        e.preventDefault(); // Prevent default button behavior
        const cartItems = [];
    
        // Loop through each row with the class 'table_row'
        $('.table_row').each(function () {
            const $row = $(this); // Current row
            console.log('Processing row:', $row); // Debug: Log the row being processed
    
            // Adjust the selector to match your data-product-id location
            const productId = $row.find('.how-itemcart1').data('product-id'); // Get product ID
            const category = $row.find('.how-itemcart1').data('category'); // Get product category
            const name = $row.find('.how-itemcart1').data('name'); // Get product name
            const size = $row.find('.how-itemcart1').data('size'); // Get product size
            const color = $row.find('.how-itemcart1').data('color'); // Get product color
            const quantity = parseInt($row.find('input.num-product').val(), 10) || 0; // Get quantity
    
            console.log('Product ID:', productId, 'Quantity:', quantity); // Debug: Log values
    
            // Add to cartItems if productId is valid and quantity is non-negative
            if (productId && category && quantity > -1) {
                cartItems.push({ productId, quantity, category, color, name, size });
            }
        });
    
        console.log('Final cartItems:', cartItems); // Debug: Log final cartItems array
    
        if (cartItems.length === 0) {
            alert('No items to update.');
            return;
        }
    
        // Send AJAX request to update the cart
        $.ajax({
            url: '/updateCart', // Ensure this endpoint exists and is correctly set up
            method: 'POST',
            contentType: 'application/json',
            data: JSON.stringify({ cartItems }),
            success: function (response) {
                console.log('Cart updated successfully:', response);
                alert('Cart updated successfully!');
                location.reload(); // Reload the page to reflect updates
            },
            error: function (xhr) {
                console.error('Error updating cart:', xhr.responseText);
                alert('Error updating cart. Please try again.');
            },
        });
    });

    
    
    
    // Add this at the top of your main.js file
    $(document).ready(function() {
        console.log('Document ready');
        
        // Test selectors
        console.log('Number of table rows:', $('.table_row').length);
        console.log('Number of quantity inputs:', $('.num-product').length);
        console.log('Update cart button exists:', $('.js-update-cart').length > 0);
        
        // Test if data attributes are present
        $('.table_row').each(function(index) {
            console.log(`Row ${index} product ID:`, $(this).attr('data-product-id'));
        });
    });

    if (typeof jQuery === 'undefined') {
        console.error('jQuery is not loaded!');
    }

    
    
    

    

    /*==================================================================
    [ +/- num product ]*/
    $('.btn-num-product-down').on('click', function(){
        var numProduct = Number($(this).next().val());
        if(numProduct > 0) $(this).next().val(numProduct - 0.5);
    });

    $('.btn-num-product-up').on('click', function(){
        var numProduct = Number($(this).prev().val());
        $(this).prev().val(numProduct + 0.5);
    });



    $('.wrap-rating').each(function(){
        var item = $(this).find('.item-rating');
        var rated = -1;
        var input = $(this).find('input');
        $(input).val(0);

        $(item).on('mouseenter', function(){
            var index = item.index(this);
            var i = 0;
            for(i=0; i<=index; i++) {
                $(item[i]).removeClass('zmdi-star-outline');
                $(item[i]).addClass('zmdi-star');
            }

            for(var j=i; j<item.length; j++) {
                $(item[j]).addClass('zmdi-star-outline');
                $(item[j]).removeClass('zmdi-star');
            }
        });

        $(item).on('click', function(){
            var index = item.index(this);
            rated = index;
            $(input).val(index+1);
        });

        $(this).on('mouseleave', function(){
            var i = 0;
            for(i=0; i<=rated; i++) {
                $(item[i]).removeClass('zmdi-star-outline');
                $(item[i]).addClass('zmdi-star');
            }

            for(var j=i; j<item.length; j++) {
                $(item[j]).addClass('zmdi-star-outline');
                $(item[j]).removeClass('zmdi-star');
            }
        });
    });
    
    /*==================================================================
    [ Show modal1 ]*/
        // Handle the 'Quick View' button click event
    $('.js-show-modal1').on('click', function(e) {
        e.preventDefault();  // Prevent the default behavior (navigation)
        
        // Get the URL from the href attribute
        var productUrl = $(this).attr('href');
        
        // Show the modal
        $('.js-modal1').addClass('show-modal1');
        
        // Make an AJAX call to fetch the product details view
        $.ajax({
            url: productUrl,
            method: 'GET',
            success: function(response) {
                // Load the response (HTML view) into the modal content
                $('#modal-content').html(response);
            },
            error: function() {
                $('#modal-content').html('<p>Error loading product details.</p>');
            }
        });
    });

    // Handle modal close
    $('.js-hide-modal1').on('click', function() {
        $('.js-modal1').removeClass('show-modal1');
        $('#productDetails').html('');
    });

    $('.js-deleteproduct-b2').on('click', function(e){
        e.preventDefault();
    });



    /*==================================================================
    [ delete product  ]*/
    $('.js-deleteproduct-b2').each(function () {
        var nameProduct = $(this).parent().parent().find('.js-name-b2').html();
       // Get the URL from the href attribute
       var productUrl = $(this).attr('href');
    
        $(this).on('click', function () {
            // Confirm deletion with a popup
            swal({
                title: "Are you sure?",
                text: "You are about to delete " + nameProduct,
                icon: "warning",
                buttons: true,
                dangerMode: true,
            }).then((willDelete) => {
                if (willDelete) {
                    // AJAX call to delete the product
                    $.ajax({
                        url: productUrl,
                        type: 'DELETE',
                        success: function (response) {
                            swal(nameProduct, "has been successfully deleted!", "success");
    
                            // Optionally remove the product from the DOM or update the UI
                            $(this).closest('.product-item').remove(); // Adjust selector based on your HTML structure
                        
                            // Redirect to the home page
                            window.location.href = '/';
                        },
                        error: function (xhr) {
                            swal("Error", "There was an issue deleting the product.", "error");
                            console.error('Error:', xhr.responseText);
                        }
                    });
                }
            });
        });
    });
    

    $('.js-addwish-detail').each(function(){
        var nameProduct = $(this).parent().parent().parent().find('.js-name-detail').html();

        $(this).on('click', function(){
            swal(nameProduct, "sa is added to wishlist !", "success");

            $(this).addClass('js-addedwish-detail');
            $(this).off('click');
        });
    });

 
    

})(jQuery);