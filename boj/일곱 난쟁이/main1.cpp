#include <bits/stdc++.h>

using namespace std;

int main(){
    int num[9] = {0, };
    int sum = 0;

    for(int i=0;i<9;i++){
        cin >> num[i];
        sum += num[i];
    }

    for(int i=0; i<9-1; i++){

        if(sum - num[i] <= 100)
            continue;

        for(int j=i+1; j<9; j++){
            if(sum - num[i] - num[j] == 100){
                num[i] = 0;
                num[j] = 0;
                // goto End;
            }
        }
        
    }

    sort(&num[0], &num[8]);
    // End:
    // int tmp=0;
    // for(int i=0; i<9-1; i++){
    //     for(int j=i+1; j<9; j++){
    //         if(num[i] > num[j]){
    //             tmp = num[i];
    //             num[i] = num[j];
    //             num[j] = tmp;
    //         }
    //     }
    // }

    for(int i=2; i<9; i++){
        cout << num[i] << endl;
    }

    return 0;
}