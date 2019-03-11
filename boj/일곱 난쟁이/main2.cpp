/*

왕비를 피해 일곱 난쟁이들과 함께 평화롭게 생활하고 있던 백설공주에게 위기가 찾아왔다. 일과를 마치고 돌아온 난쟁이가 일곱 명이 아닌 아홉 명이었던 것이다.

아홉 명의 난쟁이는 모두 자신이 "백설 공주와 일곱 난쟁이"의 주인공이라고 주장했다. 뛰어난 수학적 직관력을 가지고 있던 백설공주는, 다행스럽게도 일곱 난쟁이의 키의 합이 100이 됨을 기억해 냈다.

아홉 난쟁이의 키가 주어졌을 때, 백설공주를 도와 일곱 난쟁이를 찾는 프로그램을 작성하시오.
*/
#include <bits/stdc++.h>

using namespace std;

int main(){

    int num[9] = {0, };
    int sum=0;
    int correct[7] = {0, };

    for(int i=0;i<9;i++){
        cin >> num[i];
    }

    for(int i=0;i<3;i++){
        for(int j=i+1;j<4;j++){
            for(int k=j+1;k<5;k++){
                for(int l=k+1;l<6;l++){
                    for(int m=l+1;m<7;m++){
                        for(int n=m+1;n<8;n++){
                            for(int o=n+1;o<9;o++)
                                if(num[i]+num[j]+num[k]+num[l]+num[n]+num[m]+num[o]==100){
                                    correct[0] = num[i];
                                    correct[1] = num[j];
                                    correct[2] = num[k];
                                    correct[3] = num[l];
                                    correct[4] = num[m];
                                    correct[5] = num[n];
                                    correct[6] = num[o];
                                }
                        }
                    }
                }
            }
        }
    }
    int tmp = 0;
    for(int i=0; i<7-1; i++){
        for(int j=i+1; j<7; j++){
            if(correct[i]>correct[j]){
                tmp = correct[i];
                correct[i] = correct[j];
                correct[j] = tmp;
            }
        }
    }

    for(int i=0; i<7; i++){
        cout << correct[i] << endl;
    }

    return 0;
}