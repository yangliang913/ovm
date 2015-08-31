function is_feature_enabled(feature_set, feature){
    var val = eval("feature_set.features."+feature);
    //alert(val)
    if (val === true || val === "true" || val === "yes" || val === 1){
        return true;
    }
    // if not present in feature set assume it is allowed
    if (val === undefined || val === null){
        return true
    }
    
    return false;

}