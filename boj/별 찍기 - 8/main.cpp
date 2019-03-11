#include<bits/stdc++.h>
using namespace std;

int main(){

    int num, border;
    cin >> num;

    for(int i=1; i<=2*num-1; i++){
        border = (i<=num) ? i : 2*num-i;
        for(int j=0; j<border; j++) cout << "*";
        for(int j=0; j<2*num-2*border; j++) cout << " ";
        for(int j=0; j<border; j++) cout << "*";
        cout << endl;
    }
    return 0;
}