#include<bits/stdc++.h>
using namespace std;
int main(){
    float exch[4][4] = {{1,0.5,1.45,0.75},{1.95,1,3.1,1.49},{0.67,0.31,1,0.48},{1.34,0.64,1.98,1}};

    /// Enumerate all possibilities from (0,0,0,0) to (3,3,3,3)
    float maxval = -1;
    for(int n = 0; n < 256; n++){
        int arr[6];
        arr[0] = arr[5] = 3;
        int k = n;
        for(int i = 0; i < 4; i++){
            arr[4-i] = (n % 4);
            n /= 4;
        }
        n = k;
        if(arr[5] != 3){
            continue;
        }
        float val = 1;
        for(int j = 1; j < 6; j++){
            ///cout << exch[arr[j-1]][arr[j]] << " ";
            val *= exch[arr[j-1]][arr[j]];
        }
        maxval = max(maxval, val);
        if(maxval == val){
            cout << n << ": ";
            for(int j = 0; j < 6; j++){
                cout << arr[j] << " ";
            }
            cout << ": " << val << "\n";
        }
    }
    return 0;
}
