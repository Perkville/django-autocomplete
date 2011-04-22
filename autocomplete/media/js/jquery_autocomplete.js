(function( window, undefined ) {

var $ = window.jQuery || window.django.jQuery,
    django = window.django || {};

$.widget( "ui.djangoautocomplete", {
    options: {
        source: "../autocomplete/$name/",
        multiple: false,
        force_selection: true,
        highlight: true,
        zebra: true,
        autoFocus: true,
        delimiter: "",
        minLength: 1,
        cache: true,
        renderItem: function( ul, item) {
            return $( "<li></li>" )
                .data( "item.autocomplete", item )
                .append( $( "<a></a>" ).append( item.label ) )
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
            return $('<div/>').html(val).html();
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
            var deliRegex = new RegExp(self.options.delimiter + "+\\s+")
            var trimRegex = new RegExp(self.options.delimiter + "*\\s+$")
    		function split( val ) {
                val = val.replace(trimRegex, "");
    			return val.split(deliRegex);
    		}
            var terms = split(this.element.val());
            var termsSelect = terms;
    		function extractCurrent( term ) {
                var new_terms = split(term);
                for (idx=0; idx<new_terms.length; idx++) {
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
                if ( self.options.multiple ) {
                    if ( $.inArray( ui.item.id, self.values ) < 0 ) {
                        $('<li></li>')
                            .addClass( "ui-autocomplete-value" )
                            .data( "value.autocomplete", ui.item.id )
                            .append( '<a href="#">x</a>' + ui.item.value )
                            .appendTo( self.values_ul );
                        self._addZebra(self.values_ul);
                        self.values.push( ui.item.id );
                    }
                    return false;
                } else if (multiField) {
       				var new_terms = split( this.value );
                    var selectionStart = 0;
                    var deliLength = self.options.delimiter.length + 1;
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
            				this.value = termsSelect.join( self.options.delimiter + " " );
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
    		ul.outerWidth( this.element.outerWidth() );
        }
    
        this._initSource();
        if ( this.options.multiple ) {
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
            if ( self.options.multiple ) {
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
                            $('<li></li>')
                            .addClass("ui-autocomplete-value")
                            .data("value.autocomplete", query)
                            .append('<a href="#">x</a>' + data)
                            .appendTo(self.values_ul);
                            self._addZebra(self.values_ul);
                            self.values.push( query );
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
        if ( this.options.multiple ) {
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
        elem.find("li.ui-menu-item-alternate")
        .removeClass("ui-menu-item-alternate").end()
        .find("li.ui-autocomplete-value:odd").addClass("ui-menu-item-alternate");
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
        this.values_ul = this.element.nextAll( "ul.ui-autocomplete-values" );
        this.lastSelected = { id: null, value: null };
        if ( this.values.length && this.values_ul[0] ) {
            this.values_ul.children().each(function(i) {
                $(this)
                    .addClass( "ui-autocomplete-value" )
                    .data( "value.autocomplete", self.values[i] )
                    .prepend( '<a href="#">x</a>' );
            });
        } else {
            this.values_ul = $( "<ul></ul>" ).appendTo( this.element.parent() );
        }
        // On DOM ready, move list to the end
        $(function() {
            self.values_ul.appendTo( self.element.parent() );
        });
        this.values_ul.addClass( "ui-autocomplete-values" );
        this._addZebra(this.values_ul);
        $( ".ui-autocomplete-value a", this.values_ul[0] ).live( "click", function() {
            var span = $(this).parent();
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
    }
});


django.autocomplete = function (id, options) {
    return $(id).djangoautocomplete(options);
};

window.django = django;

})(window);
