/**
 * BIGSI search
 */
require('./commons');
require('../css/main.css');
var List = require('list.js');

var Handlebars = require('handlebars');

$(function () {

    var MAX_LEN = 5000; // TODO load from env.
    var MIN_LEN = 50; // TODO load from env.
    var API_URL = 'http://localhost:8000/search'; // TODO load from env.

    var MSG_TYPE = {
        ERROR: 'error',
        SUCCESS: 'success',
        WARNING: 'warning',
    }

    //var resultsTableTpl = Handlebars.compile($('#results-template').html());
    var alertTpl = Handlebars.compile($('#alert-template').html());

    // -- DOM Elements --//
    var $sequence = $('#sequence');
    var $threshold = $('#threshold');

    var $form = $('#search-form');
    var $searchButton = $('#search-button');
    var $clearButton = $('#clear-button');
    var $fastaFile = $('#fasta-file');

    var $example = $('#example-seq');
    var $messageContainter = $('#message-containter');
    var $loading = $('.loading');

    var $resultsSection = $('#results-section');
    var $resultsContainter = $('#results');

    var options = {
        valueNames: [
            'sample_name',
            'percent_kmers_found',
            'num_kmers',
            'num_kmers_found'
        ],
        item: '<tr>' +
            '<td class="sample_name"></td>' +
            '<td class="percent_kmers_found"></td>' +
            '<td class="num_kmers"></td>' +
            '<td class="num_kmers_found"></td>' +
            '</tr>',
        page: 20,
        pagination: true
    };

    var table = new List('results', options);

    /**
     * Load an example sequence.
     */
    $example.click(function (event) {
        event.preventDefault();
        $sequence.val(
            '>GUT_GENOME119949_7\n' +
            'GGAGTGCGGCGGAAAGTTAACCTATGCCGGACCCTGCGGGAATCCAGCTGCGTTCGAACA' +
            'AGCAACCAACATATATATCTGAATTTGGATGTGGTGGGCACTTTGTTGTTAGGCGCTTTG' +
            'AGGTGCGAGTGACACTTTGGGGTGCGCGGAGCCCTGGGTTGGGTCGATGATTTGGGATGA' +
            'GCTTCTTACTTAGGTGAAGAGGGGCTTTATGGCTGAGAGGTAGTCTTTGGCTACGTCGGC' +
            'TTTATCTGCTTGGAAATTGTGCCAGGCCCACCATTGGACCATTCCTACGAAGCTTGAGGC' +
            'TATGTGGTGTAGTAGGAAGCTTCGGTCCATGGTGGCGGCGGGGCCGTTTGGGTCGGTAGG' +
            'GACGGTTTCGGCTGCTCGGGCCATGATGGTCTTGCGGAGGCTGTCGGCGAAGACGCGTGA' +
            'ACCGGCGCCGGCTACCAGTGCCCGTACACCCTGACGGCGCTCCCAGAGGTTGTTGAGGAT' +
            'ATGCTCGACCTGTACGAGTGGGTCATCGAGGGGCGTACCGTCATCGTCGAGGGCATGGGT' +
            'GCAGATATCGCGCACGAGCTCAGCGAGCAGGTCATCTTTGCTTTTGAAGAGGCCGTAGAA' +
            'CGTGGCCCGACCCACATGGGCGCGAGCGATGATGTCGCCGACGGTGATCTTGCCGTAGTC' +
            'CTCTTCGCGCAGCAGCTCGGAGAACGCCGCGACGATCGCGGCGCGGCTTTTGGCCTTGCG' +
            'GGCATCCATGGCTATGCGTCCGCGTCAACGAGCAGACAGCGGAGCGTCCCGGAGCAGCCC' +
            'TCGTAGGGGCGCTTGCCGGCGCCGTAGCCGACGGCTTCGATGCGGTAGCGTGAGGGCAGT' +
            'TGGTCGGACGTGCGCAGAGCAGTGACGATGGCGGCGCCCGTGGGCGTCACGAGCTCGCCG' +
            'GCGACCGGTGCAGGCGTGAGGGCGATATTGCCCGCCTGGCACAGGTTGACGACAGCGGGG' +
            'ACGGGAATGGGCATGAGGCCGTGGGCGCAGCGAATGGCGCCGTGGCCCTCGAAAAGCGAC'
        )
    });

    /**
     * Submit the search to the API microservice.
     * The service expects a fasta or a DNA sequence shorter than MAX_SEQ 
     */
    $form.submit(function (event) {
        event.preventDefault();

        $searchButton.prop('disabled', true);

        var sequence = cleanSequence($sequence.val());
        var threshold = parseFloat($threshold.val());

        if (!validateSequence(sequence)) {
            showMessage('Invalid sequence. It has to be a valid DNA sequence longer than ' +
                MIN_LEN + 'pb and shorter than ' +
                MAX_LEN + 'pb', MSG_TYPE.ERROR);
            clear();
            return;
        }

        if (threshold < 0.1 || threshold > 1.0) {
            showMessage('Invalid threshold. The value has to be between 0.1 and 1.0 (recommended value 0.4)',
                MSG_TYPE.ERROR);
            clear();
            return;
        }

        $loading.show();
        table.clear();

        $.ajax({
            method: 'POST',
            url: API_URL,
            data: {
                seq: sequence,
                threshold: threshold
            }
        }).done(function (data) {
            $resultsSection.removeClass('hidden');
            table.add(data.results);
            $([document.documentElement, document.body]).animate({
                scrollTop: $resultsContainter.offset().top - 120 // header and table header
            }, 1000);
        }).fail(function (error) {
            showMessage(error.response, MSG_TYPE.ERROR);
        }).always(clear);
    })

    /**
     * Load the content of the file directly into the text area.
     */
    $fastaFile.change(function () {
        var files = $fastaFile.prop('files');
        if (files.length !== 1) {
            showMessage('Please, select only one file.', MSG_TYPE.WARNING);
            return;
        }
        var file = files[0];
        var reader = new FileReader();
        reader.onload = function () {
            $sequence.val(reader.result);
        }
        reader.onerror = function (event) {
            showMessage('File upload error. Error: ' + event.type, MSG_TYPE.ERROR);
        }
        reader.onabort = function () {
            showMessage('File upload abort.', MSG_TYPE.WARNING);
        }
        reader.readAsText(file);
    });

    /**
     * Restore form submission and hide spinner.
     */
    function clear() {
        $loading.hide();
        $searchButton.prop('disabled', false);
    }

    /**
     * Clear the form and remove the resutls table.
     */
    $clearButton.click(function () {
        $sequence.val('');
        table.clear();
        $resultsSection.addClass('hidden');
        $form.trigger('reset');
        $searchButton.prop('disabled', false);
    })

    /**
     * Will clean the fasta sequence.
     * This will remove the fasta seq name and will remove new lines or empty spaces
     * @param {string} sequence fasta or DNA sequence
     */
    function cleanSequence(sequence) {
        if (!sequence) {
            return sequence;
        }
        return sequence.replace(/^>.+\n/gm, '')
            .replace(/r\n|\n|\r|\s/gm, '');
    }

    /**
     * Will validate if the sequence is DNA only.
     * @param {string} sequence true if the sequence contains only IUPAC CNA valid characters 
     *                          and if shorter that MAX_LEN
     *                          and if longer that MIN_LEN
     */
    function validateSequence(sequence) {
        return sequence.length < MAX_LEN &&
            sequence.length > MIN_LEN &&
            /^[ATGCRYMKSWHBVDN\s]+$/i.test(sequence);
    }

    /**
     * Show a meesage to the user.
     * @param {string} message the string message
     * @param {messageType} type the message type 
     */
    function showMessage(message, type) {
        if (type === MSG_TYPE.SUCCESS) {
            $messageContainter.html(alertTpl({ message: message, type: 'success' }));
        } else if (type === MSG_TYPE.ERROR) {
            $messageContainter.html(alertTpl({ message: message, type: 'warning' }));
        };
    }
});