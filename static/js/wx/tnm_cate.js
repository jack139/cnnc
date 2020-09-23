$(function(){
    var session_id = $("#session_id").val();
    var parent_id = $("#parent_id").val();

    wx_interface(
        "tnm_cate",
        {
            session_id : session_id,
            cate_id : parent_id,
        },
        function(data){

            var tr_html;
            $.each(data['data'], function(index, i){
                if (i['type']=='cancer'){
                    tr_html += "<tr><td>";
                    tr_html += i['gen'] + '<a href="/wx/tnm_init?session_id=' + session_id + '&page_id=' + i['_id'] 
                        + '&parent_id=' + i['_id'] + '">' 
                        + i['tnm_name'] + '</a>';
                    tr_html += "</td></tr>";
                } else if (i['type']=='cancer_category') {
                    tr_html += "<tr><td>";
                    tr_html += '<a href="/wx/tnm_cate_init?session_id=' + session_id
                        + '&parent_id=' + i['cate_id'] + '">' 
                        + i['name'] + '</a>';
                    tr_html += "</td></tr>";
                } else {
                    tr_html += "<tr><td>" + i['name'] + "</td></tr>";                    
                }

            });

            $("#table_body").html(tr_html);

        }
    );

});


