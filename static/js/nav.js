document.addEventListener("DOMContentLoaded", function() {
    const mainMenuItems = document.querySelectorAll(".nav-item");
    
    mainMenuItems.forEach(function(item) {
        const submenu = item.querySelector(".submenu");
        item.addEventListener("click", function() {
            if (submenu.style.display === "block") {
                submenu.style.display = "none";
            } else {
                submenu.style.display = "block";
            }
        });
    });

    setCurrentLinkActive();
});
function setCurrentLinkActive(){
    const currentURL = window.location.href.replace(/\/$/, '');
    var currentLink = currentURL.substring(currentURL.lastIndexOf('/') + 1).split("?")[0];
    const navLinks = document.querySelectorAll(".nav-link:not(.nav-main)");
    navLinks.forEach(function(link) {
        var linkURL = link.getAttribute("href").replace(/\/$/, '');
        linkURL = linkURL.substring(linkURL.lastIndexOf('/') + 1);
        if (currentLink==linkURL) {
            link.classList.add("active");
            const parentSubMenu = link.closest(".submenu");
            if (parentSubMenu){
                parentSubMenu.style.display = "block";
            }
        }
    });
}