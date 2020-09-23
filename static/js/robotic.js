var node_history=[];

function append_option(data){
    if (data.length==0){
        node_history.pop(); // 多增加了一个历史节点，要弹出
        alertify.warning('无后续节点!'); 
        return;
    }

    $("#node_list").empty(); // 先删除所有选项        

    $.each(data, function(index, v){
        $("#node_list").append("<p><input class='option_list' type='radio' id='" + v['node_id']
            + "' value='" + v['node_id'] + "' name='options' /> "
            + "<span style='color:gray;'>[" + v['page_code'] + "]</span> " + v['text']+"</p>");
    });

    $(".option_list").click(function(event){
        var this_id = event.target.id;
        query_node(this_id);
    });
}


function query_node(node_id){

    $.ajax({
        type: "POST",
        url: "/doct/robotic",
        async: true,
        timeout: 15000,
        data: {node_id:node_id},
        dataType: "json",
        complete: function(xhr, textStatus)
        {
            if(xhr.status==200){
                var retJson = JSON.parse(xhr.responseText);
                if (retJson["ret"]==0){
                    //alertify.success('已成功保存！'); 
                    node_history.push(node_id); // 记录历史节点
                    append_option(retJson["data"]);
                }
                else{
                    alertify.error('获取数据失败：'+retJson["msg"]); 
                }
            }
            else{
                alertify.error('网络异常!'); 
            }
        }
    });

}


function first_init(){
    var start_node = $("#start_node").val();

    query_node(start_node);

    $('#back_button').click(function(){
        var last_node = node_history.pop();

        if (last_node==start_node){
            node_history.push(last_node);
            alertify.warning('已经到起点，不能再后退!'); 
        }
        else{
            var last_node2 = node_history.pop();
            query_node(last_node2);
        }
    });
}
