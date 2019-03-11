/*두 양의 정수가 주어졌을 때, 두 수 사이에 있는 정수를 모두 출력하는 프로그램을 작성하시오.*/
#include<bits/stdc++.h>

using namespace std;

int main(){

    unsigned long long num[2] = {0, };

    scanf("%llu %llu", &num[0], &num[1]);
    // cin >> num[0] >> num[1];
    sort(num, num+2);

    if(num[0] == num[1])
        cout << 0 << endl;
    else
        cout << num[1] - num[0] - 1 << endl;

    for(unsigned long long i=num[0]+1 ;i<num[1]; i++)
        cout << i << " ";

    return 0;
}
