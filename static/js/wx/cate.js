$(function(){
    var session_id = $("#session_id").val();
    var parent_id = $("#parent_id").val();

    wx_interface(
        "cate",
        {
            session_id : session_id,
            parent_id : parent_id,
        },
        function(data){
            if (data["last_dir_name"].length>0){
                $("h4_title").text(data["last_dir_name"]);
            }

            var tr_html;
            $.each(data['data'], function(index, i){
                tr_html += "<tr><td>";
                if (i['page_type']==2){
                    tr_html += i['gen'] + '<a href="/wx/doct_init?session_id=' + session_id + '&page_id='+i['link_page_id']
                        +'&parent_id='+data['parent_id']+'">'
                        +i['link_note']+'（'+i['link_name']+'）</a>';
                }
                else if (i['page_type']==1){
                    if (data['last_dir_name']=='')
                        if (i['dir_note'].length>0)
                            tr_html += i['gen'] + '<a href="/wx/cate2_init?session_id=' + session_id 
                                + '&parent_id=' + i['_id'] +'">' + i['dir_name'] + '</a><span style="float:right;">'+ i['dir_note'] + '</span>';
                        else
                            tr_html += i['gen'] + '<a href="/wx/cate2_init?session_id=' + session_id 
                                + '&parent_id=' + i['_id'] +'">' + i['dir_name'] + '</a>';
                    else
                        tr_html += i['gen'] + i['dir_name'];
                }
                else {
                    tr_html += i['gen'] + '<a href="/wx/doct_init?session_id=' + session_id + '&page_id=' + i['_id'] 
                        + '&parent_id=' + data['parent_id'] + '">' 
                        + i['page_name'] + '（' + i['page_code'] + '）</a>';
                }
                tr_html += "</td></tr>";

            });

            $("#table_body").html(tr_html);

            if (data['last_dir_name']!=''){
                $("#div_return").show();
            }
        }
    );

});


