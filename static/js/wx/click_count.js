$(function(){
    wx_interface(
        "click_count",
        {
        },
        function(data){
            $("#click_count").text(data['c']);
        }
    );
});


function wx_interface(interface2, parameter2, todo_func){  /* parameter2 is dict */
    $.ajax({
        type: "POST",
        url: "/wx/"+interface2,
        async: true, 
        timeout: 15000,
        data: parameter2,
        dataType: "json",
        complete: function(xhr, textStatus)
        {
            if(xhr.status==200){
                var retJson = JSON.parse(xhr.responseText);
                if (retJson["ret"]==0){
                    todo_func(retJson["data"]);
                }
                else{
                    //alertify.error('获取数据失败：'+retJson["msg"]);
                }
            }
            else{
                //alertify.error('网络异常!'); 
            }
        }
    });
}
