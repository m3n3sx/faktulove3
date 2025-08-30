// Quick dropdown fix
$(document).ready(function() {
    console.log('🔧 Dropdown fix loading...');
    
    // Force Bootstrap dropdown initialization
    setTimeout(function() {
        $('[data-bs-toggle="dropdown"]').each(function() {
            $(this).on('click', function(e) {
                e.preventDefault();
                e.stopPropagation();
                
                var $menu = $(this).next('.dropdown-menu');
                $('.dropdown-menu').not($menu).hide();
                $menu.toggle();
            });
        });
        
        $(document).on('click', function(e) {
            if (!$(e.target).closest('.dropdown').length) {
                $('.dropdown-menu').hide();
            }
        });
        
        console.log('✅ Dropdown fix applied');
    }, 1000);
});