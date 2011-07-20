(function( window, undefined ) {

var $ = window.jQuery || window.django.jQuery,
    django = window.django || {};

$.widget( "ui.djangoautocomplete", {
    options: {
        source: "../autocomplete/$name/",
        multiple: false,
        force_selection: true,
        delimiterList: true,
        highlight: true,
        zebra: true,
        autoFocus: true,
        delimiter: "",
        minLength: 1,
        cache: true,
        renderItem: function( ul, item) {
            var content = $( "<li></li>" );
            $.each(item.label.split('\t'), function(i, v) {
                content.append($('<a></a>').append(v));
            });
            return content
                .data( "item.autocomplete", item )
                .appendTo( ul );
        }

    },
    _create: function() {
        var self = this;
        this.hidden_input = this.element.prev( "input[type=hidden]" );
        this.name = this.hidden_input.attr( "name" );
 		var queryCache = {};
		var	lastXhr;
        var accents = {
            "àåáâäãåą": "a",
            "èéêëę": "e",
            "ìíîïı": "i",
            "òóôõöøő": "o",
            "ùúûü": "u",
            "çćč": "c",
            "żźž": "z",
            "śşš": "s",
            "ñń": "n",
            "ýŸ": "y",
            "ł": "l",
            "đ": "d",
            "ğ": "g",
        };
        function convertEntities(val) {
            return $('<div/>').html(val).html().replace('&nbsp;', ' ');
        }
        function stripAccents(term) {
            term = convertEntities(term).toLowerCase();
            $.each(accents, function(accent) {
                term = term.replace(new RegExp("[" + accent + "]", "g"), accents[accent])
            });
            return term;
        }
        var multiField = this.options.delimiter && !self.options.multiple && !self.options.force_selection;
        if (multiField) {
            if (self.options.delimiterList) {
                var delimiterList = true;
                multiField = false;
            } else {
                var deliRegex = new RegExp('(?:' + self.options.delimiter.replace(' ', '(?: | )') + ")+\\s*")
                var trimRegex = new RegExp('(?:' + self.options.delimiter.replace(' ', '(?: | )') + ")*\\s*$")
                function split(val){
                    val = val.replace(trimRegex, "");
                    return val.split(deliRegex);
                }
                var terms = split(this.element.val());
                var termsSelect = terms;
                function extractCurrent(term){
                    var new_terms = split(term);
                    for (idx = 0; idx < new_terms.length; idx++) {
                        if (terms[idx] !== new_terms[idx]) {
                            return new_terms[idx];
                        }
                    }
                    return "";
                }
                
                // Don't navigate away from the field on tab when selecting an item
                this.element.bind("keydown", function(event){
                    if (event.keyCode === $.ui.keyCode.TAB &&
                    $(this).data("autocomplete").menu.active) {
                        event.preventDefault();
                    }
                });
            }
        }
        this.element.autocomplete({
            appendTo: this.element.parent(),
			// Add SelectFirst, need jquery.ui >= 1.8.11
			autoFocus: this.options.autoFocus,
			minLength: this.options.minLength,
            source: function(request, response) {
                var term = request.term;
                if (multiField) {
    				term = extractCurrent(request.term);
                    terms = split(self.element.val());
                    if (terms.length === 1) {
                        terms = [];
                    }
                }
				if ( self.options.cache && term in queryCache ) {
					response( queryCache[ term ] );
					return;
				}
				lastXhr = $.getJSON( this.options.sourceURL,
                                    {term: term},
                                    function( data, status, xhr ) {
					if ( xhr === lastXhr ) {
                        if (self.options.highlight) {
                            $.each(data, function(idx, result){
                                if (term) {
                                    var label = stripAccents(result.label);
                                    var stripTerm = stripAccents(term);
                                    var parts = label.split(new RegExp("(?!<[^<>]*)(" +
                                        $.ui.autocomplete.escapeRegex(stripTerm) +
                                        ")(?![^<>]*>)", "gi"));
                                    if (parts.length > 1) {
                                        label = [];
                                        var pos = 0;
                                        for (var i=0; i<parts.length; i++) {
                                            var part = parts[i];
                                            if (part === stripTerm) {
                                                label.push("<strong>" + result.label.substring(pos, pos + part.length) + "</strong>");                                                
                                            } else {
                                                label.push(result.label.substring(pos, pos + part.length));                                                
                                            }
                                            pos += part.length;
                                        }
                                        result.label = label.join("");
                                    }
                                }
                            });
                        }
    					queryCache[ term ] = data;
    					response( data );
					}
				});
            },
			// Add Zebra
			open: function( event, ui ) {
              if (self.options.zebra) {
                  $(this).autocomplete("widget").find("ui-menu-item-alternate")
                  .removeClass("ui-menu-item-alternate").end()
                  .find("li.ui-menu-item:odd a").addClass("ui-menu-item-alternate");
              }
	        },
			search: function() {
				// Custom minLength that support multiple terms
                if (multiField) {
                    termsSelect = terms;
    				var term = extractCurrent( this.value );
    				if ( term.length < self.options.minLength ) {
                        terms = split(this.value);
    					return false;
    				}
                }
			},
			focus: function() {
				// prevent value inserted on focus
                if (multiField) {
                    return false;
                }
			},
            select: function( event, ui ) {
                self.lastSelected = ui.item;
                if ( delimiterList ) {
                    if ( $.inArray( ui.item.value, self.values ) < 0 ) {
                        self._buildValueRow(ui.item.value, ui.item.value);
                    }
                    return false;
                } else if (self.options.multiple) {
                    if ($.inArray(ui.item.id, self.values) < 0) {
                        self._buildValueRow(ui.item.id, ui.item.value);
                    }
                    return false;
                } else if (multiField) {
       				var new_terms = split( this.value );
                    var selectionStart = 0;
                    var deliLength = self.options.delimiter.length;
                    for (idx=0; idx<new_terms.length; idx++) {
                        if (termsSelect[idx] !== new_terms[idx]) {
            				// add the selected item
                            if (new_terms.length > termsSelect.length) {
                                termsSelect.splice(idx, 0, ui.item.value);
                            } else {
                                termsSelect[idx] = ui.item.value;
                            }
            				// add placeholder to get the delimiter-and-space at the end
                            if (termsSelect.length === idx + 1) {
                				termsSelect.push( "" );
                            } else {
                                deliLength = 0;                                
                            }
                            terms = termsSelect;
            				this.value = termsSelect.join( self.options.delimiter );
                            selectionStart += ui.item.value.length + deliLength;
                            this.setSelectionRange(selectionStart, selectionStart);
                            break;
                        }
                        selectionStart += new_terms[idx].length + deliLength;
                    }
    				return false;
                }
            }
        }).data( "autocomplete" )._renderItem = this.options.renderItem;
        // Override _resizeMenu to always set it to the size of the input box
        this.element.data( "autocomplete" )._resizeMenu = function() {
    		var ul = this.menu.element;
            ul.wrapInner('<div></div>');
    		ul.outerWidth( this.element.outerWidth() );
        }
        // Override menu move function to support the <div> around the <li>s.
        this.element.data( "autocomplete" ).menu.move = function(direction, edge, event) {
    		if (!this.active) {
    			this.activate(event, this.element.find(edge));
    			return;
    		}
    		var next = this.active[direction + "All"](".ui-menu-item").eq(0);
    		if (next.length) {
    			this.activate(event, next);
    		} else {
    			this.activate(event, this.element.find(edge));
    		}
    	}
        this._initSource();
        if ( delimiterList ) {
            this._initDelimiterList();
        } else if (this.options.multiple) {
            this._initManyToMany();
        } else {
            this.lastSelected = {
                id: this.hidden_input.val(),
                value: this.element.val()
            };
        }
        if (this.options.force_selection) {
            this.element.focusout(function() {
                if ( self.element.val() != self.lastSelected.value ) {
                    self.element.val( "" );
                }
            });
        }
        this.element.closest( "form" ).submit(function() {
            if (delimiterList) {
                self.hidden_input.val(self.values.join(self.options.delimiter));
            } else if ( self.options.multiple ) {
                self.hidden_input.val( self.values.join(",") );
            } else if ( self.options.force_selection ) {
                self.hidden_input.val( self.element.val() ? self.lastSelected.id : "" );
            } else {
                self.element.val(self.element.val().replace(trimRegex, ""));
                self.hidden_input.val( self.element.val() );
            }
        });
        if (self.options.multiple || self.options.force_selection) {
            var hidden_value = self.hidden_input.val();
            var lookupXhr;
            var intervalID;
            
            function lookup(query){
                if (self.options.multiple) {
                    query = query.split(',').pop();
                }
                lookupXhr = $.getJSON(self.options.source, {
                    lookup: query
                }, function(data, status, xhr){
                    if (xhr === lookupXhr) {
                        if (self.options.multiple) {
                            self._buildValueRow(query, data);
                        } else {
                            self.element.val(data);
                            self.lastSelected.value = data;
                            self.lastSelected.id = query;
                        }
                        hidden_value = self.hidden_input.val();
                    }
                });
            };
            
            function check(){
                check_value = self.hidden_input.val();
                if (check_value && check_value != hidden_value) {
                    clearInterval(intervalID);
                    lookup(check_value);
                }
            }
            
            $(function() {
                self.element.nextAll( "a.related-lookup, a.add-another" )
                .click(function() {
                    intervalID = window.setInterval(check, 200);
                })
                .blur(function() {
                    clearInterval(intervalID);
                });
            });
        }

    },
    
    destroy: function() {
        this.element.autocomplete( "destroy" );
        if ( this.options.multiple || (this.options.delimiter && this.options.delimiterList) ) {
            this.values_ul.remove();
        }
		$.Widget.prototype.destroy.call( this );
    },

    _setOption: function( key, value ) {
		$.Widget.prototype._setOption.apply( this, arguments );
        if ( key === "source" ) {
            this._initSource();
        }
    },

    _initSource: function() {
        var source = typeof this.options.source === "string" ?
            this.options.source.replace( "$name", this.hidden_input.attr("name") ) :
            this.options.source;
        this.element.autocomplete( "option", "sourceURL", source );
    },

    _addZebra: function(elem) {
        elem.find(".ui-menu-item-alternate")
        .removeClass("ui-menu-item-alternate").end()
        .find(".ui-autocomplete-value:odd").addClass("ui-menu-item-alternate");
    },
    
    _buildValueRow: function(id, value, oneRow) {
        var self = this;
        $('<tr></tr>')
        	.addClass("ui-autocomplete-value")
        	.data("value.autocomplete", id)
        	.append('<td>' + value.replace('\t', '</td><td>') + '</td><td><a href="#">x</a></td>')
        	.appendTo(self.values_ul);
        if (oneRow !== false) {
            self._addZebra(self.values_ul);
            self.values.push(id);
        }
    },

    _addRemoveOnClick: function() {
        var self = this;
        $( ".ui-autocomplete-value a", this.values_ul[0] ).live( "click", function() {
            var span = $(this).closest('tr');
            var id = span.data( "value.autocomplete" );
            $.each( self.values, function (i, v) {
                if (v === id) {
                    self.values.splice(i, 1);
                }
            });
            span.remove();
            self._addZebra(self.values_ul);
            return false;
        });
    },

    _initManyToMany: function() {
        var self = this;
        this.element.bind( "autocompleteclose", function( event, ui ) {
            self.element.val( "" );
        });
        this.values = [];
        if ( this.hidden_input.val() !== "" ) {
            $.each(this.hidden_input.val().split( "," ), function(i, id) {
                self.values.push( parseInt(id, 10) );
            });
        }
        this.values_ul = this.element.nextAll( "table.ui-autocomplete-values" );
        this.lastSelected = { id: null, value: null };
        if ( this.values.length && this.values_ul[0] ) {
            this.values_ul.find('tr').each(function(i) {
                $(this)
                    .addClass( "ui-autocomplete-value" )
                    .data( "value.autocomplete", self.values[i] )
                    .append( '<td><a href="#">x</a></td>' );
            });
        } else {
            this.values_ul = $( "<table></table>" ).appendTo( this.element.parent() );
        }
        // On DOM ready, move list to the end
        $(function() {
            self.values_ul.appendTo( self.element.parent() );
        });
        this.values_ul.addClass( "ui-autocomplete-values" );
        this._addZebra(this.values_ul);
        this._addRemoveOnClick();
    },
    
    _initDelimiterList: function() {
        var self = this;
        this.autocomplete = this.element.data('autocomplete');
        this.element.val( "" );
        this.values = [];
        if ( this.hidden_input.val() !== "" ) {
            $.each(this.hidden_input.val().split( this.options.delimiter ), function(i, value) {
                self.values.push( $.trim(value) );
            });
        }
        this.lastSelected = { id: null, value: null };
        this.values_ul = $( '<table class="ui-autocomplete-values"></table>' ).appendTo( this.element.parent() );
        if ( this.values.length ) {
            $(this.values).each(function(index, value) {
                this._buildValueRow(value, value, false);
            })
        }
        // On DOM ready, move list to the end
        $(function() {
            self.values_ul.appendTo( self.element.parent() );
        });
        this._addZebra(this.values_ul);
        if (this.options.autoFocus) {
            this.element.bind( "autocompleteclose", function( event, ui ) {
                self.element.val( "" );
            });
        } else {
            // Add the typed text on enter
            var delimiter = this.options.delimiter;
            // Support both normal spaces and non-breaking spaces
            // if there's spaces in the delimiter
            if (delimiter.indexOf(' ') !== -1) {
                delimiter = new RegExp(delimiter.replace(' ', '(?: | )'));
            }
            this.element.bind("keydown", function(event){
                if (event.keyCode === $.ui.keyCode.ENTER &&
                !self.autocomplete.menu.active) {
                    event.stopImmediatePropagation();
                    var values = $(this).val().split(delimiter);
                    $(this).val("");
                    self.autocomplete.close();
                    $.each(values, function(index, value) {
                        if ( $.inArray( value, self.values ) < 0 ) {
                            $('<tr></tr>')
                                .addClass( "ui-autocomplete-value" )
                                .data( "value.autocomplete", value )
                                .append('<td>' + value + '</td><td><a href="#">x</a><td>')
                                .appendTo( self.values_ul );
                                self._addZebra(self.values_ul);
                            self.values.push( value );
                        }
                    });
                    return false;
                }
            });
        }
        this._addRemoveOnClick();
    }
});


django.autocomplete = function (id, options) {
    return $(id).djangoautocomplete(options);
};

window.django = django;

// Activate autocomplete on dynamically added row in inlines in admin.
$(window).load(function() {
    // Get all the inlines
    $('.inline-group').each(function() {
        var inlineGroup = $(this);
        var acWidgets = [];
        // For each inlines check for autocomplete input in the empty form
        inlineGroup.find('.empty-form .ui-autocomplete-input').each(function() {
            var ac = $(this);
            // Copy the script tag and restore the pre-autocomplete state
            var script = ac.nextAll('script');
            acWidgets.push(script);
            script.remove();
            ac.nextAll('ul.ui-autocomplete').remove();
            ac.before($('<input id="' + ac.attr('id') + '" type="text" />'));
            ac.remove();
        });
        if (acWidgets.length > 0) {
            inlineGroup.find('.add-row a').attr('href', '#').click(function() {
                // Find the current id #
                var num = $('#id_' + inlineGroup.attr('id').replace(/group$/, 'TOTAL_FORMS')).val() - 1;
                $.each(acWidgets, function() {
                    // Clone the script tag, add the id # and append the tag
                    var widget = $(this).clone();
                    widget.text(widget.text().replace('__prefix__', num));
                    inlineGroup.append(widget);
                });
            });
        }
    });
});

})(window);
