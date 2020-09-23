var modified=false;
var BOX_WIDTH=120,
    P_WIDTH=25,
    P_HEIGHT=80;
var graph = new joint.dia.Graph;
var node_dict={};

var paper = new joint.dia.Paper({

    el: document.getElementById('paper'),
    width: 1800,//Math.max($(document).width()*0.9,1200),
    height: Math.max($(document).height()*0.8, 700),
    gridSize: 1,
    model: graph,
    snapLinks: true,
    linkPinning: false,
    embeddingMode: false,
    background: { color: '#EFEFEF' },
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
    defaultLink: new joint.dia.Link({
        attrs: {
            '.marker-target': {
                fill: '#4B4F6A',//箭头颜色
                d: 'M 10 0 L 0 5 L 10 10 z'//箭头样式
            }
        }
    }),

    validateConnection: function(sourceView, sourceMagnet, targetView, targetMagnet) {

        return sourceMagnet != targetMagnet;
    }
});

// 双击节点修改节点内容
paper.on('cell:pointerdblclick', function(cellView, evt, x, y) {
    var c = cellView.model
    var attr = c.attributes;
    if (attr.type!='devs.Atomic') return; // 不处理连线
    
    if (attr.original_text=='0'){
        alertify.error("起始节点不能修改！");
        return;
    }
    //console.log(attr.id + ' ' + attr.attrs[".label"].text);
    //console.log(attr.original_text);
    //console.log(attr.node_question);
    
    var q_checked = '';
    if (attr.node_question.check){
        q_checked = 'checked';
    }
    var dlgContentHTML = '<div id="dlgContentHTML"><p> 节点内容 </p>'+ 
        '<textarea class="ajs-input" rows="5" id="node_note">'+attr.original_text+'</textarea>'+ 
        '<p> 节点说明（可不填） </p>'+ 
        '<input class="ajs-input" id="node_prop" type="text" value="'+attr.node_prop+'"/> '+ 
        '<p> 节点权重 </p>'+ 
        '<input class="ajs-input" id="node_weight" type="text" value="'+attr.node_weight+'"/> '+ 
        '<p> 内容有疑问 '+ 
        '<input id="node_question" type="checkbox" '+q_checked+' /> </p></div>';
    
    dlgContentHTML += '<div><textarea rows="8" class="ajs-input" style="width: -webkit-fill-available;">';
    $.each(attr.node_question.correct,function(i,value){
        //dlgContentHTML += '<div><a href="#" title="'+value.note+'">'+value.time_t+'</a></div>';
        dlgContentHTML += "----- "+value.time_t+" -----\n"+value.note+"\n";
    });
    dlgContentHTML += '</textarea></div>';

    //console.log(dlgContentHTML);

    if ($("#dlgContentHTML").length>0){
        $('#node_note').val(attr.original_text);
        $('#node_prop').val(attr.node_prop);
        $('#node_weight').val(attr.node_weight);
        $('#node_question').prop("checked", attr.node_question.check);
    }

    /* Now instead of making a prompt Dialog , use a Confirm Dialog */
    alertify.confirm2(dlgContentHTML).set('onok', function(closeevent, value) { 
        var node_note = $('#node_note').val().trim();
        var node_prop = $('#node_prop').val().trim();
        var node_weight = $('#node_weight').val().trim();
        var node_question = $('#node_question').is(":checked");

        if (node_note=='0') {  // 
            alertify.error("节点名称不能为“0”！");
        }
        else {
            if (node_note=='*' || node_note=='+') {  // 虚节点
                c.resize(P_WIDTH, P_HEIGHT);
                c.attr('.label/text', node_note);
            }
            else{
                var new_note = ((node_prop.length>0)?"{"+node_prop+"} ":"")+node_note;
                var text2 = joint.util.breakText(new_note, { width: BOX_WIDTH }); // 根据宽度折行
                var lines = (text2.match(/\n/g) || []).length + 1; // 计算 \n
                var height = 10+14*lines;

                c.resize(BOX_WIDTH, height);
                c.attr('.label/text', text2);
                c.attr('.label/fill', (!node_question)?"#000":"#ff0000");
            }
            attr.original_text = node_note;
            attr.node_prop = node_prop;
            attr.node_weight = node_weight;
            attr.node_question.check = node_question;
            //alertify.success('已修改');

            modified=true;
        }
                                    
    }).set('title',"修改节点内容");

})


// 单击右键删除节点
paper.on('cell:contextmenu', function(cellView, evt, x, y) {
    var c = cellView.model
    var attr = c.attributes;
    if (attr.type!='devs.Atomic') return; // 不处理连线

    if (attr.original_text=="0"){
        alertify.error('不能删除初始节点！');
    } else {
        alertify.confirm("确认删除", "真要删除此节点吗？("+attr.original_text+")",
            function(){
                c.remove();
                alertify.warning('节点已删除！');

                modified=true;
            },
            function(){}
        );
    }
})

// 双击空白处 新建节点
paper.on('blank:pointerdblclick', function(evt, x, y) {
    //console.log('pointerdblclick on a blank area in the paper.');
    new_box('新节点', x, y, ['i'], ['o'], '', '', '1', {check:false, correct:[]});
    alertify.success('已创建新节点');

    modified=true;
})

/* 整个图拖动： 支持鼠标 */
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
});
    
$("#paper").mousemove(function(event) {
        if (dragStartPosition)
            paper.translate(
                event.offsetX - dragStartPosition.x, 
                event.offsetY - dragStartPosition.y
            );
});

var connect = function(source, sourcePort, target, targetPort, vertices) {

    var link = new joint.shapes.devs.Link({
        source: {
            id: source.id,
            port: sourcePort
        },
        target: {
            id: target.id,
            port: targetPort
        },
        vertices : vertices,
        attrs: {
            '.marker-target': {
                fill: '#4B4F6A',//箭头颜色
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
                'fill' : (!node_question.check)?"#000":"#ff0000",
            }
        }
    });

    /*
    // Listening for changes of the position to a single element
    rect.on('change:position', function(element1, position) {
      console.log(position.x + ',' + position.y);
    });
    */
    
    graph.addCells([rect]);

    return rect;

}

// 自动计算高度
var new_box = function(text, pos_x, pos_y, in_port, out_port, node_id, node_prop, node_weight, node_question) {
    if (text.trim()=='*' || text.trim()=='+' || text.trim()=='0') {  // 虚节点
        return new_box0(text, P_WIDTH, P_HEIGHT, pos_x, pos_y, in_port, out_port, text, node_id, node_prop, node_weight, node_question);
    }
    else{ 
        var new_note = ((node_prop.length>0)?"{"+node_prop+"} ":"")+text;
        var text2 = joint.util.breakText(new_note, { width: BOX_WIDTH}); // 根据宽度折行
        var lines = (text2.match(/\n/g) || []).length + 1; // 计算 \n
        var height = 10+14*lines;

        return new_box0(text2, BOX_WIDTH, height, pos_x, pos_y, in_port, out_port, text, node_id, node_prop, node_weight, node_question);
    }
}


$(function(){
    $('#save_button').click(function(){
        $("#save_button").prop('disabled', true);

        var page_id = $("#page_id").val();
        var element_data = JSON.stringify(graph.getElements());
        var link_data = JSON.stringify(graph.getLinks());

        alertify.confirm('请确认...', '确定要保存当前数据吗？', 
            function(){ 
                $.ajax({
                    type: "POST",
                    url: "/plat/page_map",
                    async: true,
                    timeout: 15000,
                    data: {page_id:page_id, element_data:element_data, link_data:link_data},
                    dataType: "json",
                    complete: function(xhr, textStatus)
                    {
                        if(xhr.status==200){
                            var retJson = JSON.parse(xhr.responseText);
                            if (retJson["ret"]>=0){
                                alertify.success('已成功保存！'); 
                                if (retJson["ret"]>0){
                                    alertify.alert('请确认...', retJson["msg"]);
                                }

                                modified=false;
                            }
                            else{
                                alertify.error('保持数据失败：'+retJson["msg"]); 
                            }
                        }
                        else{
                            alertify.error('网络异常!'); 
                        }

                        $("#save_button").prop('disabled', false);
                    }
                });

            }, function(){ $("#save_button").prop('disabled', false); } ); 
    });

    $('#back_button').click(function(){
        if (modified){
             alertify.confirm("尚未保存", "规则树有修改，不保存就退出编辑吗？",
                function(){
                    history.go(-1);
                },
                function(){ }
            );
           
        }
        else {
            history.go(-1);
        }
    });


    // init map data
    var page_id = $("#page_id").val();

    $.ajax({
        type: "POST",
        url: "/plat/json_map",
        async: true,
        timeout: 15000,
        data: {page_id:page_id},
        dataType: "json",
        complete: function(xhr, textStatus)
        {
            if(xhr.status==200){
                var retJson = JSON.parse(xhr.responseText);
                if (retJson["ret"]==0){
                    
                    $.each(retJson["data"],function(i,value){
                        //alert(i+"..."+value);
                        if (value['text']=='0')
                            node_dict[value['_id']] = new_box(value['text'], value['position']['x'], value['position']['y'], [], ['o'], value['_id'],
                                value['node_prop'], value['node_weight'], value['node_question']);
                        else
                            node_dict[value['_id']] = new_box(value['text'], value['position']['x'], value['position']['y'], ['i'], ['o'], value['_id'],
                                value['node_prop'], value['node_weight'], value['node_question']);
                    });

                    if (retJson["connect"].length>0){
                        $.each(retJson["connect"],function(i,value){
                            connect(node_dict[value['source']], 'o', node_dict[value['target']], 'i', value['vertices']);
                        });                        
                    }
                    else {  /* 兼容旧数据 */
                        $.each(retJson["data"],function(i,value){
                            $.each(value['child'],function(j,x){
                                connect(node_dict[value['_id']], 'o', node_dict[x], 'i');
                            });
                        });
                    }
                }
                else{
                    alertify.warning(retJson["msg"]);
                }
            }
            else{
                alertify.error("网络异常！请稍后再试");
            }
        }
    });

});



/**
 * Confirm dialog object
 *
 *  alertify.confirm(message);
 *  alertify.confirm(message, onok);
 *  alertify.confirm(message, onok, oncancel);
 *  alertify.confirm(title, message, onok, oncancel);
 */
alertify.dialog('confirm2', function () {

    var autoConfirm = {
        timer: null,
        index: null,
        text: null,
        duration: null,
        task: function (event, self) {
            if (self.isOpen()) {
                self.__internal.buttons[autoConfirm.index].element.innerHTML = autoConfirm.text + ' (&#8207;' + autoConfirm.duration + '&#8207;) ';
                autoConfirm.duration -= 1;
                if (autoConfirm.duration === -1) {
                    clearAutoConfirm(self);
                    var button = self.__internal.buttons[autoConfirm.index];
                    var closeEvent = createCloseEvent(autoConfirm.index, button);

                    if (typeof self.callback === 'function') {
                        self.callback.apply(self, [closeEvent]);
                    }
                    //close the dialog.
                    if (closeEvent.close !== false) {
                        self.close();
                    }
                }
            } else {
                clearAutoConfirm(self);
            }
        }
    };

    function clearAutoConfirm(self) {
        if (autoConfirm.timer !== null) {
            clearInterval(autoConfirm.timer);
            autoConfirm.timer = null;
            self.__internal.buttons[autoConfirm.index].element.innerHTML = autoConfirm.text;
        }
    }

    function startAutoConfirm(self, index, duration) {
        clearAutoConfirm(self);
        autoConfirm.duration = duration;
        autoConfirm.index = index;
        autoConfirm.text = self.__internal.buttons[index].element.innerHTML;
        autoConfirm.timer = setInterval(delegate(self, autoConfirm.task), 1000);
        autoConfirm.task(null, self);
    }


    return {
        main: function (_title, _message, _onok, _oncancel) {
            var title, message, onok, oncancel;
            switch (arguments.length) {
            case 1:
                message = _title;
                break;
            case 2:
                message = _title;
                onok = _message;
                break;
            case 3:
                message = _title;
                onok = _message;
                oncancel = _onok;
                break;
            case 4:
                title = _title;
                message = _message;
                onok = _onok;
                oncancel = _oncancel;
                break;
            }
            this.set('title', title);
            this.set('message', message);
            this.set('onok', onok);
            this.set('oncancel', oncancel);
            return this;
        },
        setup: function () {
            return {
                buttons: [
                    {
                        text: alertify.defaults.glossary.ok,
                        key: -1, //keys.ENTER,
                        className: alertify.defaults.theme.ok,
                    },
                    {
                        text: alertify.defaults.glossary.cancel,
                        key: 27, //keys.ESC,
                        invokeOnClose: true,
                        className: alertify.defaults.theme.cancel,
                    }
                ],
                focus: {
                    element: 0,
                    select: false
                },
                options: {
                    maximizable: false,
                    resizable: false
                }
            };
        },
        build: function () {
            //nothing
        },
        prepare: function () {
            //nothing
        },
        setMessage: function (message) {
            this.setContent(message);
        },
        settings: {
            message: null,
            labels: null,
            onok: null,
            oncancel: null,
            defaultFocus: null,
            reverseButtons: null,
        },
        settingUpdated: function (key, oldValue, newValue) {
            switch (key) {
            case 'message':
                this.setMessage(newValue);
                break;
            case 'labels':
                if ('ok' in newValue && this.__internal.buttons[0].element) {
                    this.__internal.buttons[0].text = newValue.ok;
                    this.__internal.buttons[0].element.innerHTML = newValue.ok;
                }
                if ('cancel' in newValue && this.__internal.buttons[1].element) {
                    this.__internal.buttons[1].text = newValue.cancel;
                    this.__internal.buttons[1].element.innerHTML = newValue.cancel;
                }
                break;
            case 'reverseButtons':
                if (newValue === true) {
                    this.elements.buttons.primary.appendChild(this.__internal.buttons[0].element);
                } else {
                    this.elements.buttons.primary.appendChild(this.__internal.buttons[1].element);
                }
                break;
            case 'defaultFocus':
                this.__internal.focus.element = newValue === 'ok' ? 0 : 1;
                break;
            }
        },
        callback: function (closeEvent) {
            clearAutoConfirm(this);
            var returnValue;
            switch (closeEvent.index) {
            case 0:
                if (typeof this.get('onok') === 'function') {
                    returnValue = this.get('onok').call(this, closeEvent);
                    if (typeof returnValue !== 'undefined') {
                        closeEvent.cancel = !returnValue;
                    }
                }
                break;
            case 1:
                if (typeof this.get('oncancel') === 'function') {
                    returnValue = this.get('oncancel').call(this, closeEvent);
                    if (typeof returnValue !== 'undefined') {
                        closeEvent.cancel = !returnValue;
                    }
                }
                break;
            }
        },
        autoOk: function (duration) {
            startAutoConfirm(this, 0, duration);
            return this;
        },
        autoCancel: function (duration) {
            startAutoConfirm(this, 1, duration);
            return this;
        }
    };
});




