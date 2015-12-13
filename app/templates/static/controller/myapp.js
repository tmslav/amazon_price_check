var myApp = angular.module('myApp',['ngResource','ngRoute','ng']);

myApp.factory('listItems',['$resource',function($resource){
    return $resource('api',{},{
        'post':{method:'POST'},
        'get':{method:'GET'}
    })
}]);

myApp.factory('Items',['$resource',function($resource){
    return $resource('api/:id',{id:"@id"},{
        'update':{method:'PUT'},
        'get':{method:'GET'},
        'remove':{method:'DELETE'}
    });
}]);
myApp.factory('SettingsResource',['$resource',function($resource){
    return $resource("api/settings",{},{
        'post':{method:'POST'},
        'get':{method:'GET'}
    })
}]);
myApp.factory("LoadProductsAsin",["$resource",function($resource){
    return $resource("/api/addasin",{},{
        'post':{method:'POST'}
    });
}]);
myApp.factory("LoadProductsUrls",["$resource",function($resource){
    return $resource("/api/addurls",{},{
        'post':{method:'POST'}
    });
}]);

myApp.config(['$routeProvider','$locationProvider',function($routeProvider,$locationProvider){
    $routeProvider.when('/',{
        templateUrl:"/static/app/tablerow.html",
        controller:"listsController",
    }).when('/items/:item_id',{
        templateUrl:'/static/app/editrow.html',
        controller:'itemController'
    }).when('/add',{
           templateUrl:"/static/app/add.html",
            controller:"addItemController"
    }).when('/settings',{
        templateUrl:'/static/app/settings.html',
            controller:"settingController"
    }).when("/loadproducts",{
        templateUrl:'/static/app/loadproducts.html',
        controller:"loadProductsController"
    })
}]);

myApp.controller("listsController",["$scope",'$route',"$resource","$location","listItems","Items",
    function($scope,$route,$resource,$location,listItems,Items){
        var self = this;
        self.lists = $scope.lists = [];
        self.Items = Items;
        listItems.query(function (data) {
            for (i=0;i<data.length;i++){
                    self.lists.push(data[i]);
            }
        });
        $scope.click = function(item){
            $location.path("items/"+item.id);
        };

        $scope.click_x = function(index,item){
            self.lists.splice(index,1);
            Items.remove({id:item.id});

        }
}]);

myApp.controller("itemController",['$scope','$resource','$routeParams','Items',
    function($scope,$resource,$routeParams,Items){
        $scope.item = Items.get({id:$routeParams.item_id});
}]);

myApp.controller("listingController",['$scope','$resource','$location','$routeParams','Items',
    function($scope,$resource,$location,$routeParams,Items){
        $scope.Items = Items;
        $scope.location = $location;
        $scope.change = function(elem,item){
            item[elem.key]=parseInt(elem.selectedTd);
            if (!item[elem.key]){
                item[elem.key] = elem.selectedTd
            }
        };
        $scope.click = function(item){
            debugger;
            this.Items.update({id:item.id},JSON.stringify(item),function(sucess){
                location='/'
            })
        }}]);

myApp.controller("addItemController",['$scope','listItems',
    function($scope,listItems){
        $scope.item = {name:"Enter name",url:"Enter url",price:"Enter Price"};
        $scope.listItems=listItems;
        $scope.change = function(elem){
            if (elem.key=='price') {
                this.item[elem.key] = parseInt(elem.selectedTd)
            }else {
                this.item[elem.key] = elem.selectedTd
            }
        };
        $scope.click=function(){
            this.listItems.post({},JSON.stringify(this.item),function(sucess){
                location="/"
            })
        }
}]);

myApp.controller("settingController",["$scope","SettingsResource",function($scope,SettingsResource){
     var that = this;
     that.settings = $scope.settings = {
        "Send to":"",
        "Send from":"",
        "Email username":"",
        "Email password":"",
        "Amazon user":"",
        "Access key ID":"",
        "Secret Access key":""
    };

    that.keys = [
        "Send to",
        "Send from",
        "Email username",
        "Email password",
        "Amazon user",
        "Access key ID",
        "Secret Access key"
    ];

    SettingsResource.get({},function(settings){
        for(i=0;i<that.keys.length;i++) {
            that.settings[that.keys[i]] = settings[that.keys[i]];
        }
    });

    $scope.click = function() {
        SettingsResource.post({}, JSON.stringify(this.settings), function () {
            location="/"
        });

    };
    $scope.change = function(elem){
            if (elem.key=='price') {
                this.settings[elem.key] = parseInt(elem.selectedTd)
            }else {
                this.settings[elem.key] = elem.selectedTd
            }
        };


}]);

myApp.controller("loadProductsController",["$scope","LoadProductsAsin","LoadProductsUrls",
    function($scope,LoadProductsAsin,LoadProductsUrls){
        var that = this;
        that.scope = $scope;
        that.urls = $scope.urls;
        that.asins = $scope.asins;
        $scope.Asin = LoadProductsAsin;
        $scope.Urls = LoadProductsUrls;

        $scope.click = function(elem,text){
            if (text=='asins'){
                asins = this.asins.split("\n");
                this.Asin.post({},asins,function(){
                    location="/";
                });
            }else{
                debugger;
                urls = this.urls.split("\n")
                this.Urls.post({},urls,function(){
                    location="/"
                });
            }
        }
}]);