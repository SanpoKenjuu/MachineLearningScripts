/**
 * @param {SVGElement} svg
 * @param {Function} callback
 * @param {jsPDF} callback.pdf
 * */
function svg_to_pdf(svg, callback) {
  svgAsDataUri(svg, {}, function(svg_uri) {
    var image = document.createElement('img');

    image.src = svg_uri;
    image.onload = function() {
      var canvas = document.createElement('canvas');
      var context = canvas.getContext('2d');
      var doc = new jsPDF('p', 'pt', 'letter');
      var dataUrl;

      canvas.width = image.width;
      canvas.height = image.height;
      context.drawImage(image, 0, 0, image.width, image.height);
      /*
      var imgData=context.getImageData(0,0,canvas.width,canvas.height);
      var data=imgData.data;
      for(var i=0;i<data.length;i+=4){
          if(data[i+3]<255){
              data[i]=255;
              data[i+1]=255;
              data[i+2]=255;
              data[i+3]=255;
          }
      }
      context.putImageData(imgData,0,0);*/
      dataUrl = canvas.toDataURL('image/png');
      doc.addImage(dataUrl, 'png', 0, 0, parseInt(image.width)-60, parseInt(image.height)-60);

      callback(doc);
    }
  });
}

/**
 * @param {string} name Name of the file
 * @param {string} dataUriString
*/
function download_pdf(name, dataUriString) {
  var link = document.createElement('a');
  link.addEventListener('click', function(ev) {
    link.href = dataUriString;
    link.download = name;
    document.body.removeChild(link);
  }, false);
  document.body.appendChild(link);
  link.click();
}