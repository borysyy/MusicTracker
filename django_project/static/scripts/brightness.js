$(() => {

    const colorChange = $('.color-change');

    const profileHue = $('body').css('background-color');


    
    const r = parseInt(hexColor.substring(0, 2), 16);
    const g = parseInt(hexColor.substring(2, 4), 16);
    const b = parseInt(hexColor.substring(4, 6), 16);
    
    const brightness = Math.sqrt(
        0.299 * (r * r) +
        0.587 * (g * g) +
        0.114 * (b * b)
      );
    
      console.log(brightness);

      // >186 = light background   
      let color = brightness > 186 ? "black" : "white";

      colorChange.css("color", color);
      


});