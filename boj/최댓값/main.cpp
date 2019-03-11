/*
9개의 서로 다른 자연수가 주어질 때, 이들 중 최댓값을 찾고 
그 최댓값이 몇 번째 수인지를 구하는 프로그램을 작성하시오.

예를 들어, 서로 다른 9개의 자연수

3, 29, 38, 12, 57, 74, 40, 85, 61

이 주어지면, 이들 중 최댓값은 85이고, 이 값은 8번째 수이다.
*/
#include <bits/stdc++.h>

using namespace std;

int main(){

    int num[9] = {0, };
    int max, index;

    for (int i=0; i<9 ;i++){
        cin >> num[i];
    }

    max=num[0];
    index = 0;
    for (int i=0; i<9; i++){
        if (max < num[i]){
            max = num[i];
            index = i;
        } 
    }
    index += 1;

    cout << max << endl;
    cout << index << endl;

    return 0;
}