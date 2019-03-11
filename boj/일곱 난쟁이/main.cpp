#include <bits/stdc++.h>

using namespace std;

int main(){
    int num[9] = {0, };
    int sum = 0;

    for(int i=0;i<9;i++){
        cin >> num[i];
        sum += num[i];
    }

    sort(&num[0], &num[9]);
    
    for(int i=0; i<9-1; i++){

        if(sum - num[i] <= 100)
            continue;

        for(int j=i+1; j<9; j++){
            if(sum - num[i] - num[j] == 100){
                num[i] = num[j] = 0;
                for(int k=0; k<9; k++) if(num[k]) cout << num[k] << endl;
                    return 0;
            }
        }
        
    }

    return 0;
}