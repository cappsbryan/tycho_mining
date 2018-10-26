function markActiveNavItem(itemName) {
    for (const element of document.getElementsByClassName(itemName + "-item")) {
        element.classList.add("active");
    }

    for (const element of document.getElementsByClassName(itemName + "-link")) {
        element.innerHTML += " <span class=\"sr-only\">(current)</span>";
    }
}
