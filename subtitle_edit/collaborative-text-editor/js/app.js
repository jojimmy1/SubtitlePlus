// IIFE keeps our variables private
// and gets executed immediately!
(function () {
  // make doc editable and focus
  var doc = document.getElementById('doc');
  doc.contentEditable = true;
  doc.focus();

  // if this is a new doc, generate a unique identifier
  // append it as a query param
  var id = getUrlParameter('id');
  if (!id) {
    location.search = location.search
      ? '&id=' + getUniqueId() : 'id=' + getUniqueId();
    return;
  }

  return new Promise(function (resolve, reject) {
    // subscribe to the changes via Pusher
    // var pusher = new Pusher(<INSERT_PUSHER_APP_KEY_HERE>);
    var pusher = new Pusher("280463b30a3a909dbe1c", { cluster: "us2" });
    var channel = pusher.subscribe(id);
    channel.bind('client-text-edit', function(html) {
      // save the current position
      var currentCursorPosition = getCaretCharacterOffsetWithin(doc);
      doc.innerHTML = html;
      // set the previous cursor position
      setCaretPosition(doc, currentCursorPosition);
    });
    channel.bind('pusher:subscription_succeeded', function() {
      resolve(channel);
    });
  }).then(function (channel) {
    function triggerChange (e) {
      channel.trigger('client-text-edit', e.target.innerHTML);
    }

    doc.addEventListener('input', triggerChange);
  })

  // a unique random key generator
  function getUniqueId () {
    return 'private-' + Math.random().toString(36).substr(2, 9);
  }

  // function to get a query param's value
  function getUrlParameter(name) {
    name = name.replace(/[\[]/, '\\[').replace(/[\]]/, '\\]');
    var regex = new RegExp('[\\?&]' + name + '=([^&#]*)');
    var results = regex.exec(location.search);
    return results === null ? '' : decodeURIComponent(results[1].replace(/\+/g, ' '));
  }

  function getCaretCharacterOffsetWithin(element) {
    var caretOffset = 0;
    var doc = element.ownerDocument || element.document;
    var win = doc.defaultView || doc.parentWindow;
    var sel;
    if (typeof win.getSelection != "undefined") {
      sel = win.getSelection();
      if (sel.rangeCount > 0) {
        var range = win.getSelection().getRangeAt(0);
        var preCaretRange = range.cloneRange();
        preCaretRange.selectNodeContents(element);
        preCaretRange.setEnd(range.endContainer, range.endOffset);
        caretOffset = preCaretRange.toString().length;
      }
    } else if ( (sel = doc.selection) && sel.type != "Control") {
      var textRange = sel.createRange();
      var preCaretTextRange = doc.body.createTextRange();
      preCaretTextRange.moveToElementText(element);
      preCaretTextRange.setEndPoint("EndToEnd", textRange);
      caretOffset = preCaretTextRange.text.length;
    }
    return caretOffset;
  }

  function setCaretPosition(el, pos) {
    // Loop through all child nodes
    for (var node of el.childNodes) {
      if (node.nodeType == 3) { // we have a text node
        if (node.length >= pos) {
            // finally add our range
            var range = document.createRange(),
                sel = window.getSelection();
            range.setStart(node,pos);
            range.collapse(true);
            sel.removeAllRanges();
            sel.addRange(range);
            return -1; // we are done
        } else {
          pos -= node.length;
        }
      } else {
        pos = setCaretPosition(node,pos);
        if (pos == -1) {
            return -1; // no need to finish the for loop
        }
      }
    }
    return pos; // needed because of recursion stuff
  }
})();

///////////////////////////////////////
// adding waveform below
/* global angular */

// let app = angular.module('ngWavesurfer', []);

// app.directive('ngWavesurfer', function() {
//     return {
//         restrict: 'E',

//         link: function($scope, $element, $attrs) {
//             $element.css('display', 'block');

//             let options = angular.extend({ container: $element[0] }, $attrs);
//             let wavesurfer = WaveSurfer.create(options);

//             if ($attrs.url) {
//                 wavesurfer.load($attrs.url, $attrs.data || null);
//             }

//             $scope.$emit('wavesurferInit', wavesurfer);
//         }
//     };
// });

// app.controller('PlaylistController', function($scope) {
//     let activeUrl = null;

//     $scope.paused = true;

//     $scope.$on('wavesurferInit', function(e, wavesurfer) {
//         $scope.wavesurfer = wavesurfer;

//         $scope.wavesurfer.on('play', function() {
//             $scope.paused = false;
//         });

//         $scope.wavesurfer.on('pause', function() {
//             $scope.paused = true;
//         });

//         $scope.wavesurfer.on('finish', function() {
//             $scope.paused = true;
//             $scope.wavesurfer.seekTo(0);
//             $scope.$apply();
//         });
//     });

//     $scope.play = function(url) {
//         if (!$scope.wavesurfer) {
//             return;
//         }

//         activeUrl = url;

//         $scope.wavesurfer.once('ready', function() {
//             $scope.wavesurfer.play();
//             $scope.$apply();
//         });

//         $scope.wavesurfer.load(activeUrl);
//     };

//     $scope.isPlaying = function(url) {
//         return url == activeUrl;
//     };
// });