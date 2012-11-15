// error messages
Error = function(title, text, element) {
    var messages = document.getElement('.messages').removeClass('hide');
    var message = messages.getElement('.alert-message.error').removeClass('hide');
    message.getElement('p').set('html', '<strong>{0}</strong> {1}'.substitute([title, text]));
    message.getElement('a').fireEvent('click', event, 3000);

    if (element) {
        element.getParent('.clearfix').addClass('error');
    }
};

// add events
window.addEvent('domready', function() {
    // enable smooth scrolling
    new Fx.SmoothScroll({
        'offset': { 'y': -50 },
        'links': 'a[scroll][href^="#"]',
        'wheelStops': true
    });

    // special scroll listener for the request form actions bar
    window.addEvent('scroll', function(event) {
        var scroll = window.getSize().y + window.getScroll().y;
        var form = document.getElement('form[name="request"]');
        var coordinates = form.getCoordinates();

        var element = form.getElement('.actions');

        if (scroll - 200 <= coordinates.top || scroll >= coordinates.bottom) {
            element.removeClass('fixed');
        } else {
            element.addClass('fixed');
        }
    });

    // sections
    document.getElements('a.minimize').addEvent('click', function(event) {
        event.preventDefault();

        var section = this.getParent('.page').getElement('section');

        if (section.isDisplayed()) {
            section.hide();
        } else {
            section.show();
        }
    });

});
