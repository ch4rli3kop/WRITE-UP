#include<bits/stdc++.h>
using namespace std;

int main(){

    int num, border;
    cin >> num;

    for(int i=0; i<2*num-1; i++){
        border = (i<num) ? i : 2*num-1-i-1;
        for(int j=0; j<border; j++) cout << " ";
        for(int j=0; j<2*num-1-2*border; j++) cout << "*";
        cout << endl;
    }

    return 0;
}
