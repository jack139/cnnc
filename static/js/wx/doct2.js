var node_history=[];
var node_dict={};
var node_cache={};

/* 添加连线 */
var connect = function(source, target) {
    $("#"+source+", #"+target).connections({'class':'fast'});
};



/* 生成节点 */
var new_box = function(text, pos_x, pos_y, node_id, node_prop, node_weight, node_question) {
    var div = new Node(text, pos_x, pos_y, node_id, node_prop, node_weight, node_question);
    return div;
}

function cache_node(data){ 
    var node_list = []
    $.each(data, function(index, value){
        if (node_history.indexOf(value['_id'])>-1 && node_dict.hasOwnProperty(value['_id'])){ // 规则树有成环
            node_cache[value['_id']]['repeat']++;
            value['_id'] = value['_id'] + "_" + node_cache[value['_id']]['repeat'];
        }
        if (!node_dict.hasOwnProperty(value['_id'])){
            node_dict[value['_id']] = new_box(value['text'], value['position']['x'], value['position']['y'], value['_id'],
                value['node_prop'], value['node_weight'], value['node_question']);

            value['parent'] = [];
            value['repeat'] = 0; // 当前图中相同节点重复的次数，用于成环的处理
            node_cache[value['_id']]=value;  // 缓存节点信息
        }
        node_list.push(value['_id']);
    });

    return node_list; /* return node id list */
}

function connect_child(node_id){
    $.each(node_cache[node_id]['child'],function(j,x){
        if (node_dict.hasOwnProperty(x)){
            //connect(node_dict[node_id], node_dict[x]);
            connect(node_id, x);
            if (!node_cache[x]['parent'].hasOwnProperty(node_id))
                node_cache[x]['parent'].push(node_id); // 记录父节点
        }
    });

    for (i=0;i<node_history.length-1;i++){
        //connect(node_dict[node_history[i]], node_dict[node_history[i+1]]); 
        connect(node_history[i], node_history[i+1]); 
    }
}

function query_node(node_id, include_me){
    //$(".floatLayer").show();

    var session_id = $("#session_id").val();
    var node_id2 = node_id.split("_")[0];

    wx_interface(
        "next_node",
        {
            session_id : session_id,
            node_id    : node_id2,
            include_me : include_me,
        },
        function(data){
            var children = cache_node(data);
            /* 在子节点中删除当前节点 */
            if (include_me==1){
                var index = children.indexOf(node_id);
                if (index > -1) {
                    children.splice(index, 1);
                }
                else{
                    /* 当前是起始节点，返回未包含起始节点的情况，返回第1个作为起始节点 */
                    node_id = children[0];
                    children.splice(0, 1);
                    node_history.pop(); /* 重新压入历史 */
                    node_history.push(node_id);
                }
            }
            /* 处理虚节点造成子节点数量不一致的问题 */
            //if (children.length>node_cache[node_id]['child'].length)
            node_cache[node_id]['child']=children;
            /* 画节点 */
            draw_family(node_id);
        }
    );
}


function draw_family(node_id){
    var node = node_cache[node_id];
    var cells = [];

    //graph.clear()
    $("#paper").html("");

    $.each(node_history ,function(i,x){
        if (i==0){ // 初始节点
            node_dict[x].position(40, 50);
        }

        node_dict[x].appendToPaper();
    });

    /* 画node_history最后一个节点的子节点 */

    /* 调整子节点的坐标 */
    var box = node_dict[node_id].getBBox(); 
    var offset = {x: 80, y: 50};
    var xx = box.x + box.width + offset.x;
    var child = node['child'].length;
    var max_width=$("#frame").width()-100;
    var max_height=$("#frame").height()-100;

    $.each(node['child'],function(j,y){
        if (node_dict.hasOwnProperty(y)){
            var box2 = node_dict[y].getBBox();
            var yy = box.y+box.height+offset.y;

            if (j==0){
                if (child>1 && box2.height<box.height)
                    yy = box.y;
                else{
                    if (box2.height<box.height){
                        yy = box.y+(box.height-box2.height)/2;
                    }
                    else{
                        var yy_move = (box2.height-box.height)/2;
                        yy = box.y - Math.min(yy_move, 50);
                    }

                }
            }

            node_dict[y].position(xx, yy);
            box = node_dict[y].getBBox();

            if (box.x+box.width > max_width) max_width = box.x+box.width;
            if (box.y+box.height > max_height) max_height = box.x+box.height;
        }
    });        

    /* 连线 */
    connect_child(node['_id']);  

    /* 设置当前节点边框颜色 */
    node_dict[node_id].border_color("#527382");

    /* 更新paper尺寸 */
    $("#frame").width(max_width+100);
    $("#frame").height(max_height+100);
    console.log($( "#frame" ).width() +','+ $( "#frame" ).height());

    /* 移动paper，当前节点放在屏幕中间 */
    if (node_history.length>1){
        scroll_left = screen.width<480 ? 480-screen.width : -2;
        $.scrollTo($("#"+node_id),300,{offset:{left:scroll_left,top:-100}});
        //$.scrollTo($("#"+node_id),300,{offset:{left:-40,top:-100}});
    }


}

/* 显示3层：父节点、当前节点、子节点 */
function element_touch(node_id){
    var node = node_cache[node_id];

    // 记录点击历史
    var index_of = node_history.indexOf(node['_id']);
    if (index_of==-1){
        node_history.push(node['_id']); // 记录新节点
    }
    else {
        var count_to_pop = node_history.length-index_of-1;
        for (i=0; i<count_to_pop; i++) // 不在栈顶，是父节点
            console.log(node_history.pop());
    }

    if (node['child'].length==0)
        alertify.success('已没有后续节点。', 2)

    // 检查是否有缓存
    var not_in_cache = 0;
    $.each(node['child'],function(i,x){
        if (!node_dict.hasOwnProperty(x)) not_in_cache++;
        if (node_history.indexOf(x)>-1) not_in_cache++; // 说明规则图有成环
    });

    if (not_in_cache>0){
        query_node(node['_id'], 0);
    }
    else{
        draw_family(node['_id']);
    } 

    TDAPP.onEvent("点击节点", $("#page_code").html()+' '+$("#page_name").html()); 
}


/* 页面初始化 */
$(function(){
    var session_id = $("#session_id").val();
    var parent_id = $("#parent_id").val();
    var page_code_p = $("#page_code_p").val();
    var page_id = $("#page_id").val();

    var show_cate = function(session, parent_id, page, page_code_p){
        /* 生成目录 */
        wx_interface(
            "cate",
            {
                session_id : session_id,
                parent_id  : parent_id,
            },
            function(data){
                if (data["last_dir_name"].length>0){
                    document.title=data["last_dir_name"];
                }

                var tr_html;
                var first_page_id = null;
                $.each(data['data'], function(index, i){
                    tr_html += "<tr><td>";
                    if (i['page_type']==2){
                        tr_html += i['gen'] + '<a href="/wx/doct_init?session_id=' + session_id + '&page_id=' + i['link_page_id']
                            + '&parent_id=' + data['parent_id']+'">'
                            + i['link_note'] + '（'+i['link_name']+'）</a>';

                        if (first_page_id==null) first_page_id = i['link_page_id'];
                    }
                    else if (i['page_type']==1){
                        if (data['last_dir_name']=='')
                            if (i['dir_note'].length>0)
                                tr_html += i['gen'] + '<a href="/wx/doct_init?session_id=' + session_id + '&parent_id=' + i['_id'] 
                                    +'">' + i['dir_name'] + '</a><span style="float:right;">'+ i['dir_note'] + '</span>';
                            else
                                tr_html += i['gen'] + '<a href="/wx/doct_init?session_id=' + session_id + '&parent_id=' + i['_id'] 
                                    +'">' + i['dir_name'] + '</a>';                            
                        else
                            tr_html += i['gen'] + i['dir_name'];
                    }
                    else {
                        tr_html += i['gen'] + '<a href="/wx/doct_init?session_id=' + session_id + '&page_id=' + i['_id'] 
                            + '&parent_id=' + data['parent_id'] + '">' 
                            + i['page_name'] + '（' + i['page_code'] + '）</a>';

                        if (first_page_id==null) first_page_id = i['_id'];
                    }
                    tr_html += "</td></tr>";

                });

                $("#table_body").html(tr_html);

                /* 第一次进入page_id为空， 从菜单获取并显示节点 */
                /*
                var page_id = $("#page_id").val();

                if (page_id.length==0){
                    $("#page_id").val(first_page_id);
                    show_doct(session_id, first_page_id, page_code_p);
                }
                */

            }
        );
    };

    var show_doct = function(session, page, page_code_p){
        wx_interface(
            "doct",
            {
                session_id : session,
                page_id    : page,
                page_code  : page_code_p,
            },
            function(data){
                var start_node = data['data']['start_node'];
                var page_name = data['data']['page_name'];
                var page_code = data['data']['page_code'];
                $("#version").val(data['data']['version']);
                $("#page_name").html(filterNote(page_name));
                $("#page_code").html(filterNote(page_code));

                TDAPP.onEvent("打开页面", page_code+' '+page_name);

                if (parent_id.trim().length==0)
                    parent_id = data['data']['parent_id'];

                if (data['data']['type']=='map'){
                    $("#note").hide();
                    $("#paper").show();

                    query_node(start_node, 1);
                    
                    node_history.push(start_node); // 记录初始节点

                    /* 屏幕相关 */
                    /*
                    $(window).resize(function() {
                        //alert($( window ).width() +','+ $( window ).height());
                        var w = $("#frame").width();
                        var h = $("#frame").height();
                        $("#frame").width(h);
                        $("#frame").height(w);
                    });
                    */

                    $(".sidebar.top").trigger("sidebar:open", [{ speed: 300 }]);

                    if ($(window).width()<$(window).height()) alertify.warning('提示：将手机横屏，使用效果更佳。', 2);

                }
                else{
                    $("#paper").hide();
                    $("#note").show();
                    $("#slide-out-div").hide();
                    $("#note").html(filterNote(data['data']['rich_text']));
                }

                show_cate(session_id, parent_id, page_id, page_code_p);
            }
        );
    };


    //$(".sidebar.left").sidebar().trigger("sidebar:open");
    $(".sidebar.left").sidebar({side: "left"});
    $(".sidebar.bottom").sidebar({side: "bottom"});
    $(".sidebar.top").sidebar({side: "top"});

    var startX, startY;
    $('.sidebar.bottom').on('touchstart',function(e){
        startX = e.originalEvent.changedTouches[0].pageX;
        startY = e.originalEvent.changedTouches[0].pageY;
        e.stopPropagation();
    });

    $('.sidebar.bottom').on('touchend',function(e){
        var moveEndX = e.originalEvent.changedTouches[0].pageX;
        var moveEndY = e.originalEvent.changedTouches[0].pageY;
        if (moveEndY==startY && moveEndX==startX){
            $(".sidebar.bottom").trigger("sidebar:close", [{ speed: 300 }]);
        }
        e.stopPropagation();
    });

    $('.sidebar.left').on('touchstart',function(e){
        startX = e.originalEvent.changedTouches[0].pageX;
        startY = e.originalEvent.changedTouches[0].pageY;
        e.stopPropagation();
    });

    $('.sidebar.left').on('touchend',function(e){
        var moveEndX = e.originalEvent.changedTouches[0].pageX;
        var moveEndY = e.originalEvent.changedTouches[0].pageY;
        if (moveEndY==startY && moveEndX==startX){
            $(".sidebar.left").trigger("sidebar:close", [{ speed: 300 }]);
        }
        e.stopPropagation();
    });

    $('#bar_close').on('click touchstart', function(e) {
        $(".sidebar.left").trigger("sidebar:close", [{ speed: 300 }]);
        e.stopPropagation();
    });
    $('#bar_open').on('click touchstart', function(e) {
        $(".sidebar.left").trigger("sidebar:open", [{ speed: 300 }]);
        e.stopPropagation();
    });

    /* 点框架关闭底栏 */
    $("#frame").on('click tap', function(e){
       $(".sidebar.bottom").trigger("sidebar:close", [{ speed: 300 }]); 
       $(".sidebar.left").trigger("sidebar:close", [{ speed: 300 }]);
       //e.stopPropagation();
       //e.preventDefault();
    })

    show_doct(session_id, page_id, page_code_p);

});