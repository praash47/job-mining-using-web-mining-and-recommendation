let authenticationTooltip = document.querySelector('.user-authentication')
let authenticationIcon = document.querySelector('.right-nav__profile .circular-icon')

authenticationIcon.addEventListener('click', () => {
    authenticationTooltip.classList.toggle('active')
})

let searchInputBox = document.querySelector('.right-nav__search--normal')
let searchInput = document.querySelector('.search-input input')
let searchIcon = document.querySelector('.right-nav__search--normal .circular-icon')
let searchIconImg = document.querySelector('.right-nav__search--normal .circular-icon img')

searchIcon.addEventListener('click', () => {
    searchInput.classList.toggle('active')
    searchIconImg.classList.toggle('active')

    // If width is 0, then make it 300px, and vice versa.
    if (searchInputBox.style.width == '0px' || searchInputBox.style.width == '' ) {
        searchInputBox.style.width = '300px';
    } else {
        searchInputBox.style.width = '0';
    }
})
// mobile only
let searchTooltip = document.querySelector('.right-nav__search--tooltip-box')
let outerSearchIcon = document.querySelector('.right-nav__search .circular-icon')

outerSearchIcon.addEventListener('click', () => {
    searchTooltip.classList.toggle('active')
})
// mobile only end