export function getCookie(name) {
  let cookieValue = null;
  if (document.cookie && document.cookie !== '') {
    const cookies = document.cookie.split(';');
    for (let i = 0; i < cookies.length; i += 1) {
      const cookie = cookies[i].trim();
      // Does this cookie string begin with the name we want?
      if (cookie.substring(0, name.length + 1) === (`${name}=`)) {
        cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
        break;
      }
    }
  }
  return cookieValue;
}
export function showSnackbar(snack) {
  const snackbar = snack;
  snackbar.className = 'show';

  // After 3 seconds, remove the show class from DIV
  setTimeout(() => { snackbar.className = snackbar.className.replace('show', ''); }, 3000);
}
