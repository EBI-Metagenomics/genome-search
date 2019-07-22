var $ = require('jquery');
require('ebi-framework/libraries/foundation-6/js/foundation.min');
require('ebi-framework/js/script.min');
require('ebi-framework/js/foundationExtendEBI.min');
require('ebi-framework/js/elixirBanner.min');

window.Foundation.addToJquery($);

require('../static/images/twitter_card/card_image.jpg');
require('../static/images/twitter_card/card_image_no_ebi_logo.jpg');
require('../static/images/ajax-loader.gif');

$(document).foundation();
$(document).foundationExtendEBI();
