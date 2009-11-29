function yui_autocomplete(name, ac_url, force_selection) {

    this.name = name;
    this.ac_url = ac_url;
    this.force_selection = force_selection;

    this.setup = function () {
        var datasource = new YAHOO.util.XHRDataSource(ac_url);
        datasource.responseType = YAHOO.util.XHRDataSource.TYPE_JSON;
        datasource.responseSchema = {
            resultsList: "result",
            fields: ["label", "id"]
        };

        datasource.doBeforeParseData = function (request, original, callback) {
            var parsed = {"result": []};
            for (var i in original)
                parsed.result.push({"id": original[i][0], "label": original[i][1]});
            return parsed;
        };
        datasource.resultTypeList = false;

        var input = document.getElementById("id_"+name);
        var container = document.createElement("div");
        YAHOO.util.Dom.insertAfter(container, input);
        if (!YAHOO.util.Dom.hasClass(document.body, "yui-skin-sam"))
            YAHOO.util.Dom.addClass(document.body, "yui-skin-sam");

        var autocomplete = new YAHOO.widget.AutoComplete(input, container, datasource);
        autocomplete.resultTypeList = false;
        autocomplete.queryDelay = .5;
        autocomplete.forceSelection = force_selection;

        var selected_item = {label: null, id: null};
        var hidden = document.getElementById("id_hidden_"+name);
        autocomplete.itemSelectEvent.subscribe(function (type, args) {
            selected_item = args[2];
            hidden.value = selected_item.id;
        });
        form = document.getElementsByTagName("form")[0];
        YAHOO.util.Event.addListener(form, "submit", function (event, form) {
            if (selected_item.label != input.value && !force_selection)
                hidden.value = input.value;
        });
        this.datasource = datasource;
        this.autocomplete = autocomplete;
    };
    YAHOO.util.Event.onDOMReady(this.setup, null, this);
};

autocomplete = yui_autocomplete;
