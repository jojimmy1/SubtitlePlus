// function typeInTextarea(newText, el = document.activeElement) {
//     const [start, end] = [el.selectionStart, el.selectionEnd];
//     el.setRangeText(newText, start, end, 'select');
//   }
  
//   document.getElementById("input").onkeydown = e => {
//     if (e.key === "Enter") typeInTextarea("lol");
//   }

window.onload = function(){

    function typeInTextarea(newText, el = document.activeElement) {
        const [start, end] = [el.selectionStart, el.selectionEnd];
        el.setRangeText(newText, start, end, 'select');
      }
      
      document.getElementById("input").onkeydown = e => {
        if (e.key === "Alt") typeInTextarea("lol");
      }
 
 }