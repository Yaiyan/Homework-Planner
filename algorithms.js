function quicksort(array) {
    //Note: Sorts position 1 of arrays
    
    //If array is length 1, we can't splice further
    //So return the value
    if (array.length <= 1) {
        return array;
    }
    
    //Choose the first element of the array as our pivot
    //Gives sub-par results in an almost sorted array
    //but for random array this should suffice
    var pivot = array[0][0];
    
    //Exclude pivot from search array
    var searchArray = array.slice(1,array.length);
    var low = [];
    var high = [];
    
    //Iterate through array, sort into low and high piles
    for (i=0;i<searchArray.length;i++) {
        if (searchArray[i][0] < pivot) {
            low.push(searchArray[i]);
        } else {
            high.push(searchArray[i]);
        }
    }
    
    //Call ourselves again to sort the low and high piles
    var low = quicksort(low);
    var high = quicksort(high);
    
    //Finally merge low pile, pivot (array[0]), and high pile
    return low.concat([array[0]].concat(high));
}

function quicksortString(array) {
    //Note: Sorts strings in position 2 of arrays
    
    //If array is length 1, we can't splice further
    //So return the value
    if (array.length <= 1) {
        return array;
    }
    
    //Choose the first element of the array as our pivot
    //Gives sub-par results in an almost sorted array
    //but for random array this should suffice
    var pivot = array[0][1].toLowerCase();
    
    //Exclude pivot from search array
    var searchArray = array.slice(1,array.length);
    var low = [];
    var high = [];
    
    //Iterate through array, sort into low and high piles
    for (i=0;i<searchArray.length;i++) {
        if (searchArray[i][1].toLowerCase() < pivot) {
            low.push(searchArray[i]);
        } else {
            high.push(searchArray[i]);
        }
    }
    
    //Call ourselves again to sort the low and high piles
    var low = quicksortString(low);
    var high = quicksortString(high);
    
    //Finally merge low pile, pivot (array[0]), and high pile
    return low.concat([array[0]].concat(high));
}

function binarySearch(array, val) {
    //Returns -1 if index not found
    //As it searches based on first element of 2d array
    //then array[mid][0] is used.
    //To be more general, then remove the trailing [0]
    
    //Set low and high search indexes
    lowIndex = 0;
    highIndex = array.length-1;
    
    //Whilst the lowest possible location is smaller than
    //the biggest, keep searching
    //If the lowest and biggest are equal then we haven't
    //been able to find it
    while (lowIndex <= highIndex) {
        //Choose the next index to search at
        // - we split the array in half
        searchIndex = Math.floor((lowIndex+highIndex)/2)
        
        //Check if the value is found at this index
        if (array[searchIndex][0] == val) {
            //It is, so let's return the index
            return searchIndex;
        } else if (array[searchIndex][0] < val) {
            //Too small, we should search higher numbers
            lowIndex = searchIndex+1
        } else {
            //Too big, we should search smaller numbers
            highIndex = searchIndex-1
        }
    }
    
    //Couldn't find, return -1
    return -1;
}