
function yui_autocomplete(name, ac_url) {
    YAHOO.util.Event.onDOMReady(function () {
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
        }
        datasource.resultTypeList = false;

        var select = document.getElementById("id_"+name);
        var input = document.getElementById("id_ac_"+name);

        YAHOO.util.Dom.addClass(input.parentNode, "yui-ac");

        select.style.display = "none";
        input.style.display = "block";

        var container = document.createElement("div");
        YAHOO.util.Dom.insertAfter(container, input);

        var autocomplete = new YAHOO.widget.AutoComplete(input, container, datasource);
        autocomplete.resultTypeList = false;
        autocomplete.queryDelay = .5;

        autocomplete.itemSelectEvent.subscribe(function (type, args) {
            var item = args[2];
            select.value = item.id;
        });
    });
}

autocomplete = yui_autocomplete;
