var BOX_WIDTH=150,
    P_WIDTH=25,
    P_HEIGHT=80;

var node_history=[];
var node_dict={};
var node_cache={};

var graph_size = {width:$("#paper_layout").width()-30, height:$(document).height()*0.5};

var graph = new joint.dia.Graph;

var paper = new joint.dia.Paper({

    el: $('#paper'),
    width: graph_size.width,
    height: graph_size.height,
    gridSize: 1,
    model: graph,
    snapLinks: true,
    linkPinning: false,
    embeddingMode: true,
    interactive: false,
    highlighting: {
        'default': {
            name: 'stroke',
            options: {
                padding: 6
            }
        },
        'embedding': {
            name: 'addClass',
            options: {
                className: 'highlighted-parent'
            }
        }
    },

    validateEmbedding: function(childView, parentView) {

        return parentView.model instanceof joint.shapes.devs.Coupled;
    },

    validateConnection: function(sourceView, sourceMagnet, targetView, targetMagnet) {

        return sourceMagnet != targetMagnet;
    }
});


/* 拖动： 支持鼠标和移动设备 */
var dragStartPosition;

paper.on({
    'blank:pointerdown': function(event, x, y) {
        dragStartPosition = { x: x, y: y};
        //console.log(dragStartPosition);
    },
    'blank:pointerup': function(event, x, y) {
        dragStartPosition = false;
        //console.log(dragStartPosition);
    },
    'element:pointerup': function(cellView, evt, x, y) {
        element_touch(cellView, evt, x, y);
    },
});
    
$("#paper").mousemove(function(event) {
        if (dragStartPosition)
            paper.translate(
                event.offsetX - dragStartPosition.x, 
                event.offsetY - dragStartPosition.y
            );
});


$("#paper")[0].ontouchmove = function(event){
    if (dragStartPosition){
        var rect = event.target.getBoundingClientRect();
        var x = event.targetTouches[0].pageX - rect.left;
        var y = event.targetTouches[0].pageY - rect.top;
        paper.translate(
                x - dragStartPosition.x, 
                y - dragStartPosition.y
        );
    }
    //console.log(event.touches[0].clientX, event.touches[0].clientY);
}

/* function to add cells */
var connect = function(source, sourcePort, target, targetPort) {

    var link = new joint.shapes.devs.Link({
        source: {
            id: source.id,
            port: sourcePort
        },
        target: {
            id: target.id,
            port: targetPort
        },
        attrs: {
            '.marker-target': {
                fill: '#0066CC',//箭头颜色
                d: 'M 10 0 L 0 5 L 10 10 z'//箭头样式
            }
        }
    });

    link.addTo(graph).reparent();

};

// 生成节点
var new_box0 = function(text, width, height, pos_x, pos_y, in_port, out_port, text0, node_id, node_prop, node_weight, node_question) {

    if (!text0) text0=text;

    var rect = new joint.shapes.devs.Atomic({
        node_id: node_id, // node_id from backbone code
        original_text:text0,
        node_prop:node_prop, 
        node_weight:node_weight, 
        node_question:node_question,
        position: {
            x: pos_x,
            y: pos_y
        },
        size: {
            width: width,
            height: height
        },
        inPorts: in_port,
        outPorts: out_port,
        attrs: {
            '.label': { 
                text: text,
                'ref-x': 0.5,  // a1.attr('.label/ref-x',0.5)
                'ref-y': 5,
                'fill' : (!node_question)?"#000":"#ff0000",
            }
        }
    });

    graph.addCells([rect]);

    return rect;

}

// 自动计算高度
var new_box = function(text, pos_x, pos_y, in_port, out_port, node_id, node_prop, node_weight, node_question) {
    if (text.trim()=='*' || text.trim()=='+' || text.trim()=='0') {  // 虚节点
        var text0 = text.trim();
        if (text0=='0') { text0='起\n始\n节\n点'; }
        return new_box0(text0, P_WIDTH, P_HEIGHT, pos_x, pos_y, in_port, out_port, text, node_id, node_prop, node_weight, node_question);
    }
    else{
        var max_char = 100; 
        //var new_note = (((node_prop.length>0)?"{"+node_prop+"} ":"")+text.substr(0,max_char)
        //var new_note = (node_prop.length>0)?node_prop:(text.substr(0,max_char)
        var new_note = (text.substr(0,max_char)
            +((text.length>max_char)?"...":"")).replace('\r\n','').replace('\n',''); 
        var text2 = joint.util.breakText(text2filter(new_note), { width: BOX_WIDTH}); // 根据宽度折行
        var lines = (text2.match(/\n/g) || []).length + 1; // 计算 \n
        var height = 10+14*lines;

        return new_box0(text2, BOX_WIDTH, height, pos_x, pos_y, in_port, out_port, text, node_id, node_prop, node_weight, node_question);
    }
}


function cache_node(data){ 
    var node_list = []
    $.each(data, function(index, value){
        if (node_history.indexOf(value['_id'])>-1 && node_dict.hasOwnProperty(value['_id'])){ // 规则树有成环
            node_cache[value['_id']]['repeat']++;
            value['_id'] = value['_id'] + "_" + node_cache[value['_id']]['repeat'];
        }
        if (!node_dict.hasOwnProperty(value['_id'])){
            node_dict[value['_id']] = new_box(value['text'], value['position']['x'], value['position']['y'], ['i'], ['o'], value['_id'],
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
            connect(node_dict[node_id], 'o', node_dict[x], 'i');
            if (!node_cache[x]['parent'].hasOwnProperty(node_id))
                node_cache[x]['parent'].push(node_id); // 记录父节点
        }
    });

    for (i=0;i<node_history.length-1;i++){
        connect(node_dict[node_history[i]], 'o', node_dict[node_history[i+1]], 'i'); 
    }
}

function query_node(node_id, include_me){
    $(".floatLayer").show();

    node_id2 = node_id.split("_")[0];

    $.ajax({
        type: "POST",
        url: "/ui/next_node",
        async: true, 
        timeout: 15000,
        data: {node_id:node_id2,include_me:include_me},
        dataType: "json",
        complete: function(xhr, textStatus)
        {
            if(xhr.status==200){
                var retJson = JSON.parse(xhr.responseText);
                if (retJson["ret"]==0){
                    var children = cache_node(retJson["data"]);
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
                else{
                    alertify.error('获取数据失败：'+retJson["msg"]); 
                }
            }
            else{
                alertify.error('网络异常!'); 
            }

            $(".floatLayer").hide();
        }
    });
}


function draw_family(node_id){
    var node = node_cache[node_id];
    var cells = []

    graph.clear()

    $.each(node_history ,function(i,x){
        if (i==0){ // 初始节点
            node_dict[x].position(40, 80);
        }

        cells.push(node_dict[x]);
        node_dict[x].attr("rect/stroke", 'white');

        /* 调整子节点的坐标 */
        var box = node_dict[x].getBBox(); // a.Rect {x: 100, y: 100, width: 25, height: 80}
        var offset = {x: 40, y: 20};
        var xx = box.x + box.width + offset.x;
        var child = node_cache[x]['child'].length;

        $.each(node_cache[x]['child'],function(j,y){
            if (node_dict.hasOwnProperty(y)){
                var box2 = node_dict[y].getBBox();
                var yy = box.y+box.height+offset.y;

                if (j==0){
                    if (child>1 && box2.height<box.height)
                        yy = box.y;
                    else
                        yy = (box2.height<box.height)?box.y+(box.height-box2.height)/2:box.y-(box2.height-box.height)/2;
                }

                node_dict[y].position(xx, yy);
                box = node_dict[y].getBBox();
            }
        });        
    });

    /* 画子节点 */
    $.each(node['child'],function(i,x){
        if (node_dict.hasOwnProperty(x)){
            cells.push(node_dict[x]);
            node_dict[x].attr("rect/stroke", 'white');
        }
    });

    /* 连线 */
    graph.addCells(cells);
    node_dict[node_id].attr("rect/stroke", 'red'); // 当前节点红框

    connect_child(node['_id']);  

    /* 移动paper，当前节点放在屏幕中间 */
    var node_b = node_dict[node_id].getBBox();
    paper.translate(
            graph_size.width/2 - ( node_b.x + node_b.width/2 ), 
            graph_size.height/2 - ( node_b.y + node_b.height/2 ) 
    );

}

/* 显示3层：父节点、当前节点、子节点 */
function element_touch(cell, evt, x, y){
    var node = node_cache[cell.model.attributes.node_id];

    if (cell.model.attributes.original_text[0]=="0"){ // 首节点
        $("#note").html(filterNote(cell.model.attributes.node_prop));    
    }
    else {
        $("#prop").html(text2HTML(cell.model.attributes.node_prop));
        $("#note").html(text2HTML(cell.model.attributes.original_text));
    }

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


    //console.log(node);
}


/* 页面初始化 */
$(function(){
    var start_node = $("#start_node").val();
    var page_name = $("#hidden_page_name").html();
    $("#page_name").html(filterNote(page_name));

    query_node(start_node, 1);
    
    node_history.push(start_node); // 记录初始节点
});


