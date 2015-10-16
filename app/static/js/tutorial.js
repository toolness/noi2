$(function() {
  var VERTICAL_INSET_PX = 8;
  var currStep = $("meta[name=current-tutorial-step]").attr('content');

  function positionPopup(popup, target) {
    var topArrow = $('.e-top-arrow', popup).css({left: '0'});
    var top = Math.floor(target.offset().top + target.outerHeight() +
                         topArrow.outerHeight() - VERTICAL_INSET_PX);
    var left = Math.floor(target.offset().left - topArrow.offset().left +
                          target.width() / 2 - topArrow.outerWidth() / 2);
    popup.css({top: top + 'px'});
    topArrow.css({left: left + 'px'});
  }

  function showPopup(id) {
    var target = $("[data-tutorial-target='" + id + "']");
    var popup = $("#tutorial-" + id);
    var position = positionPopup.bind(null, popup, target);

    if (!target.length) return;

    popup.addClass('m-active');
    position();
    $(window).on('resize.tutorial.popup', position);
  }

  function hidePopup(popup) {
    popup.removeClass('m-active');
    $(window).off('resize.tutorial.popup');
  }

  function postTutorialStep(step) {
    $.post('/tutorial', {
      'step': step
    });
  }

  // Advance tutorial steps
  $("[data-tutorial-step]").click(function (evt) {
    var step = $(evt.target).data('tutorial-step');
    hidePopup($(this).closest('.b-tutorial-box'));
    if (step) {
      postTutorialStep(step);
      showPopup(step);
    }
  });

  // For debugging only.
  window._resetTutorial = function() {
    postTutorialStep(1);
  }

  if (currStep) showPopup(currStep);
});
