/**
 * Get the latest completed element of a lineage.
 * For example for:
 *  'd__Bacteria;p__Bacteroidota;c__Bacteroidia;o__Bacteroidales;f__Bacteroidaceae;g__Bacteroides;s__'
 * this method will return 'g__Bacteroides'
 * @param {string} lineage a genome lineage
 */
function processLineage(lineage) {
    var split = lineage.split(';');
    for (var i = split.length - 1; i > 0; i--) {
        if (split[i].length > 3) {
            return split[i];
        }
    }
    return '';
}

module.exports = {
    processLineage: processLineage
};