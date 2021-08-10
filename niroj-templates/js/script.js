window.addEventListener('scroll', () => {
	const scrolledFromTop = window.scrollY
	
	// Shrink the header on scroll
	let header = document.querySelector('header')
	if (scrolledFromTop > 0) {
		header.classList.add('shrink')
	} else {
		header.classList.remove('shrink')
	}
})