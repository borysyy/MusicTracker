$(() => {

    const colorChange = $('.color-change');

    const profileHue = $('body').css('background-color');

    const strippedRGB = stripRGB(profileHue);

    if(strippedRGB)
    {
        const r = strippedRGB[0];
        const g = strippedRGB[1];
        const b = strippedRGB[2];
        
        const brightness = 
            (0.299 * r) +
            (0.587 * g) +
            (0.114 * b);
          
          // >186 = dark background   
          let textColor = brightness > 186 ? 'black' : 'white';
          let backgroundColor = brightness > 186 ? 'white' : 'black';
  
          colorChange.css('color', textColor);
          $('button.color-change').hover(
            function() {
              $(this).css('background-color', backgroundColor);  // Mouse enter
            },
            function() {
              $(this).css('background-color', '');  // Mouse leave - resets to original
            }
          );

    }

      function stripRGB(rgb) 
      {
        const result = rgb.match(/\d+/g);
        if (!result) return null;
        return result
          .slice(0, 3);
      }

});