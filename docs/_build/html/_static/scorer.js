// Sphinx search scorer
// Based on Sphinx's built-in scorer with some customizations

function Scorer() {
    this.objNameMatch = 11;
    this.objPartialMatch = 6;
    this.objPrefixMatch = 5;
    this.titleMatch = 15;
    this.nonTitleMatch = 2;
    this.priorityMatch = 10;
}

Scorer.prototype.score = function (result) {
    var score = 0;
    var pattern = result.pattern;
    var doc = result.doc;

    // Title matches are weighted highest
    if (doc.title && doc.title.toLowerCase().indexOf(pattern.toLowerCase()) > -1) {
        score += this.titleMatch;
    }

    // Object name matches
    if (doc.objName && doc.objName.toLowerCase().indexOf(pattern.toLowerCase()) > -1) {
        score += this.objNameMatch;
    }

    // Partial matches in object names
    if (doc.objName && doc.objName.toLowerCase().indexOf(pattern.toLowerCase()) > -1) {
        score += this.objPartialMatch;
    }

    // Prefix matches in object names
    if (doc.objName && doc.objName.toLowerCase().startsWith(pattern.toLowerCase())) {
        score += this.objPrefixMatch;
    }

    // Priority boost
    if (doc.priority && doc.priority > 0) {
        score += this.priorityMatch * doc.priority;
    }

    // Full text search
    if (doc.fulltext && doc.fulltext.toLowerCase().indexOf(pattern.toLowerCase()) > -1) {
        score += this.nonTitleMatch;
    }

    return score;
};
