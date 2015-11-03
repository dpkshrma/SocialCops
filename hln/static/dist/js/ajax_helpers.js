var base_url = "http://localhost:8080";
var api = {
	"endpoint": "",
	"action": "",
	"method": "POST"
};

var request_data = function(api, data, handlers){
	var url = [base_url,api['endpoint'], api['action']].join('/')+"/";
	$.ajax({
		url: url,
		method: api['method'],
		data: data['server'],
		dataType: 'json',
		success:function(data){
			if("data" in handlers) handlers['data'](data);
		},
		beforeSend:function(){
			if("beforeSend" in handlers) handlers['beforeSend']();
		},
		complete:function(){
			if("complete" in handlers) handlers['complete']();
		}
	});
};

var get_leads = function(args, handlers){
	api['endpoint'] = 'lead';
	api['action'] = 'get';
	data = {}
	data['server'] = {
		search_query: args['search_query'],
		count: args['count'],
		offset: args['offset']
	};
	request_data(api, data, handlers);
};

var get_reporter = function(args, handlers){
	api['endpoint'] = 'reporter';
	api['action'] = 'get';
	data = {}
	data['server'] = {
		reporter_id: args['reporter_id']
	}
	request_data(api, data, handlers);
};

var get_leadcount_agg = function(args, handlers){
	api['endpoint'] = 'lead/count';
	api['action'] = 'get';
	data = {}
	data['server'] = {
		agg_type: args['agg_type'],
		agg_size: args['agg_size'],
		time_interval: args['time_interval']
	}
	request_data(api, data, handlers);	
}

var get_leadcount = function(args, handlers){
	api['endpoint'] = 'lead/count';
	api['action'] = 'get';
	data = {}
	data['server'] = {}
	request_data(api, data, handlers);	
}

var get_reportercount = function(args, handlers){
	api['endpoint'] = 'reporter/count';
	api['action'] = 'get';
	data = {}
	data['server'] = {}
	request_data(api, data, handlers);
}