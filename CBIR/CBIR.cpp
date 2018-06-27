#include "stdafx.h"
#include <opencv2/core/core.hpp>
#include <opencv2/highgui/highgui.hpp>
#include <opencv2\opencv.hpp>
#include <iostream>
#include <math.h>
#include <stdlib.h>

using namespace cv;
using namespace std;


void calculateQueryLBP(Mat, int *);
void calculateLBP(Mat, int **, int);
void writeImages(int *, int, int);
void calculate64(Mat, int **, int);
void calculateQuery64(Mat, int *);
void calculateDistance(int *, int **, float *, int, int);
void sortCalculatedArray(int, float *, int *);
void retrieveByColor();
void retrieveByTexture();
int getIndexOf58(int);

int main()
{
	Mat image;
	int i, j, k;
	int sampleCount;
	float *distanceArray;
	int *sortedArray;
	int **rgb64bin;
	int query64bin[64] = { 0 };
	char filename[10];
	char ColorDirName[30] = "Color\\";
	char TextureDirName[30] = "Texture\\";

	k = 1;
	while (k){
		cout << "\nChoose option:\n(1)Color\n(2)Texture\n\nOption: ";
		cin >> k;
		if (k == 1){
			retrieveByColor();
			k = 0;
		}
		else if (k == 2){
			retrieveByTexture();
			k = 0;
		}
	}
}

void retrieveByColor(){
	Mat image;
	int i, j, k;
	int sampleCount;
	float *distanceArray;
	int *sortedArray;
	int **rgb64bin;
	int query64bin[64] = { 0 };
	char filename[10];
	char ColorDirName[30] = "Color\\";

	cout << "Enter color sample image count: ";
	cin >> sampleCount;

	rgb64bin = (int**)calloc(sampleCount, sizeof(int*));
	for (i = 0; i < sampleCount; i++){
		if ((rgb64bin[i] = (int*)calloc(64, sizeof(int))) == NULL){
			cout << "Couldnt allocate memory  **rgb64bin" << endl;
			return;
		}
	}
	if ((distanceArray = (float*)calloc(sampleCount, sizeof(float))) == NULL){
		cout << "Couldnt allocate memory  distanceArray" << endl;
		return;
	}
	if ((sortedArray = (int*)calloc(sampleCount, sizeof(int))) == NULL){
		cout << "Couldnt allocate memory  distanceArray" << endl;
		return;
	}
	for (i = 1; i <= sampleCount; i++){
		_itoa_s(i, filename, 10);
		strcat_s(ColorDirName, filename);
		strcat_s(ColorDirName, ".jpg");
		printf("%s\n", ColorDirName);
		image = imread(ColorDirName, CV_LOAD_IMAGE_COLOR);
		if (!image.data)                              // Check for invalid input
		{
			cout << "Could not open or find the image" << std::endl;
			system("pause");
			return;
		}

		calculate64(image, rgb64bin, i - 1);

		for (k = 0; k<30; k++){//clear buffer
			ColorDirName[k] = 0;
		}
		strcat_s(ColorDirName, "Color\\");
		for (k = 0; k<10; k++){//clear buffer
			filename[k] = 0;
		}
	}

	cout << "Image database created..." << endl;

	cout << "Enter query image name: ";
	cin >> filename;
	strcat_s(ColorDirName, filename);
	strcat_s(ColorDirName, ".jpg");
	image = imread(ColorDirName, CV_LOAD_IMAGE_COLOR);
	if (!image.data)                              // Check for invalid input
	{
		cout << "Could not open or find the image" << std::endl;
		system("pause");
		return;
	}
	calculateQuery64(image, query64bin);
	calculateDistance(query64bin, rgb64bin, distanceArray, sampleCount, 64);

	printf("\n\nDistances:\n");
	for (i = 0; i < sampleCount; i++){
		printf("i:%d>>%f\n", i, distanceArray[i]);

	}

	sortCalculatedArray(sampleCount, distanceArray, sortedArray);

	printf("sortedArray\n");
	for (i = 0; i < sampleCount; i++){
		printf("i:%d>>%d\n", i, sortedArray[i]);

	}

	writeImages(sortedArray, sampleCount, 1);
	system("pause");
	free(distanceArray);
	free(sortedArray);
	for (i = 0; i < sampleCount; i++){
		free(rgb64bin[i]);
	}
	free(rgb64bin);
}

void retrieveByTexture(){
	Mat image;
	int i, j, k;
	int sampleCount;
	float *distanceArray;
	int *sortedArray;
	int **lbpArray;
	int querylbp[59] = { 0 };
	char filename[10];
	char textureDirName[30] = "Texture\\";

	cout << "Enter color sample image count: ";
	cin >> sampleCount;

	lbpArray = (int**)calloc(sampleCount, sizeof(int*));
	for (i = 0; i < sampleCount; i++){
		if ((lbpArray[i] = (int*)calloc(59, sizeof(int))) == NULL){
			cout << "Couldnt allocate memory  **rgb64bin" << endl;
			return;
		}
	}
	if ((distanceArray = (float*)calloc(sampleCount, sizeof(float))) == NULL){
		cout << "Couldnt allocate memory  distanceArray" << endl;
		return;
	}
	if ((sortedArray = (int*)calloc(sampleCount, sizeof(int))) == NULL){
		cout << "Couldnt allocate memory  distanceArray" << endl;
		return;
	}
	for (i = 1; i <= sampleCount; i++){
		_itoa_s(i, filename, 10);
		strcat_s(textureDirName, filename);
		strcat_s(textureDirName, ".jpg");
		printf("%s\n", textureDirName);
		image = imread(textureDirName, 0);
		if (!image.data)                              // Check for invalid input
		{
			cout << "Could not open or find the image" << std::endl;
			system("pause");
			return;
		}
		
		calculateLBP(image, lbpArray, i - 1);

		for (k = 0; k<30; k++){//clear buffer
			textureDirName[k] = 0;
		}
		strcat_s(textureDirName, "Texture\\");
		for (k = 0; k<10; k++){//clear buffer
		filename[k] = 0;
		}
	}

		cout << "Image database created..." << endl;

		cout << "Enter query image name: ";
		cin >> filename;
		strcat_s(textureDirName, filename);
		strcat_s(textureDirName, ".jpg");
		image = imread(textureDirName, 0);
		if (!image.data)                              // Check for invalid input
		{
			cout << "Could not open or find the image" << std::endl;
			system("pause");
			return;
		}
		calculateQueryLBP(image, querylbp);
		calculateDistance(querylbp, lbpArray, distanceArray, sampleCount, 59);

		printf("\n\nDistances:\n");
		for (i = 0; i < sampleCount; i++){
			printf("i:%d>>%f\n", i, distanceArray[i]);
		}

		sortCalculatedArray(sampleCount, distanceArray, sortedArray);

		printf("sortedArray\n");
		for (i = 0; i < sampleCount; i++){
			printf("i:%d>>%d\n", i, sortedArray[i]);
		}

		writeImages(sortedArray, sampleCount, 2);
		system("pause");
		free(distanceArray);
		free(sortedArray);
		for (i = 0; i < sampleCount; i++){
			free(lbpArray[i]);
		}
		free(lbpArray); 
}

void calculateQueryLBP(Mat image, int querylbp[]){
	int i, j;
	int rows = image.rows;
	int cols = image.cols;
	Scalar centerPixel;
	Scalar pixel_0;
	Scalar pixel_1;
	Scalar pixel_2;
	Scalar pixel_3;
	Scalar pixel_4;
	Scalar pixel_5;
	Scalar pixel_6;
	Scalar pixel_7;
	int number;

	for (i = 1; i < rows - 1; i++){
		for (j = 1; j < cols - 1; j++){
			number = 0;
			centerPixel = image.at<uchar>(i, j);
			pixel_0 = image.at<uchar>(i - 1, j - 1);
			pixel_1 = image.at<uchar>(i - 1, j);
			pixel_2 = image.at<uchar>(i - 1, j + 1);
			pixel_3 = image.at<uchar>(i, j + 1);
			pixel_4 = image.at<uchar>(i + 1, j + 1);
			pixel_5 = image.at<uchar>(i + 1, j);
			pixel_6 = image.at<uchar>(i + 1, j - 1);
			pixel_7 = image.at<uchar>(i, j - 1);

			if (centerPixel.val[0] < pixel_0.val[0]){
				number += 128;
			}
			if (centerPixel.val[0] < pixel_1.val[0]){
				number += 64;
			}
			if (centerPixel.val[0] < pixel_2.val[0]){
				number += 32;
			}
			if (centerPixel.val[0] < pixel_3.val[0]){
				number += 16;
			}
			if (centerPixel.val[0] < pixel_4.val[0]){
				number += 8;
			}
			if (centerPixel.val[0] < pixel_5.val[0]){
				number += 4;
			}
			if (centerPixel.val[0] < pixel_6.val[0]){
				number += 2;
			}
			if (centerPixel.val[0] < pixel_7.val[0]){
				number += 1;
			}
			querylbp[getIndexOf58(number)] += 1;
		}
	}
}

void calculateLBP(Mat image, int **lbpArray, int imgNumber){
	int i, j;
	int rows = image.rows;
	int cols = image.cols;
	Scalar centerPixel;
	Scalar pixel_0;
	Scalar pixel_1;
	Scalar pixel_2;
	Scalar pixel_3;
	Scalar pixel_4;
	Scalar pixel_5;
	Scalar pixel_6;
	Scalar pixel_7;
	int number;

	for (i = 1; i < rows - 1; i++){
		for (j = 1; j < cols - 1; j++){
			number = 0;
			centerPixel = image.at<uchar>(i, j);
			pixel_0 = image.at<uchar>(i - 1, j - 1);
			pixel_1 = image.at<uchar>(i - 1, j);
			pixel_2 = image.at<uchar>(i - 1, j + 1);
			pixel_3 = image.at<uchar>(i, j + 1);
			pixel_4 = image.at<uchar>(i + 1, j + 1);
			pixel_5 = image.at<uchar>(i + 1, j);
			pixel_6 = image.at<uchar>(i + 1, j - 1);
			pixel_7 = image.at<uchar>(i, j - 1);

			if (centerPixel.val[0] < pixel_0.val[0]){
				number += 128;
			}
			if (centerPixel.val[0] < pixel_1.val[0]){
				number += 64;
			}
			if (centerPixel.val[0] < pixel_2.val[0]){
				number += 32;
			}
			if (centerPixel.val[0] < pixel_3.val[0]){
				number += 16;
			}
			if (centerPixel.val[0] < pixel_4.val[0]){
				number += 8;
			}
			if (centerPixel.val[0] < pixel_5.val[0]){
				number += 4;
			}
			if (centerPixel.val[0] < pixel_6.val[0]){
				number += 2;
			}
			if (centerPixel.val[0] < pixel_7.val[0]){
				number += 1;
			}
			lbpArray[imgNumber][getIndexOf58(number)] += 1;
		}
	}
}


void writeImages(int sortedArray[], int sampleCount, int option){
	char filename[10];
	char ColorDirName[30] = "Color\\";
	char textureDirName[30] = "Texture\\";
	Mat image;
	int i;
	int j=1;
	int k;
	for (i = 0; i < sampleCount; i++){
		for (k = 0; k<30; k++){//clear buffer
			ColorDirName[k] = 0;
		}
		if (option == 1){
			strcat_s(ColorDirName, "Color\\");
		}
		else if (option == 2){
			strcat_s(ColorDirName, "Texture\\");
		}
		
		for (k = 0; k<10; k++){//clear buffer
			filename[k] = 0;
		}
		_itoa_s(sortedArray[i]+1, filename, 10);
		strcat_s(ColorDirName, filename);
		strcat_s(ColorDirName, ".jpg");
		printf("%s\n", ColorDirName);
		image = imread(ColorDirName, CV_LOAD_IMAGE_COLOR);
		if (!image.data)                              // Check for invalid input
		{
			cout << "Could not open image" << std::endl;
			system("pause");
			return;
		}

		for (k = 0; k<30; k++){//clear buffer
			ColorDirName[k] = 0;
		}
		//strcat_s(ColorDirName, "Test\\");
		for (k = 0; k<10; k++){//clear buffer
			filename[k] = 0;
		}
		_itoa_s(j, filename, 10);
		strcat_s(ColorDirName, filename);
		strcat_s(ColorDirName, ".jpg");

		vector<int> compression_params;
		compression_params.push_back(CV_IMWRITE_JPEG_QUALITY);
		compression_params.push_back(95);
		try {
			imwrite(ColorDirName, image, compression_params);
		}
		catch (runtime_error& ex) {
			fprintf(stderr, "Exception: %s\n", ex.what());
			return;
		}
		j++;
	}
}

void calculateQuery64(Mat image, int query64bin[]){
	int i, j;
	int val64 = 0;
	Vec3b color;
	uchar blue;
	uchar green;
	uchar red;
	int rows = image.rows;
	int cols = image.cols;

	for (int i = 0; i < rows; i++){
		for (int j = 0; j < cols; j++){
			val64 = 0;
			color = image.at<Vec3b>(i, j);
			blue = color.val[0];
			green = color.val[1];
			red = color.val[2];

			if (red >= 192){ //red bits
				val64 += 48;
			}
			else if (red >= 128){
				val64 += 32;
			}
			else if (red >= 64){
				val64 += 16;
			}

			if (green >= 192){ //green bits
				val64 += 12;
			}
			else if (green >= 128){
				val64 += 8;
			}
			else if (green >= 64){
				val64 += 4;
			}

			if (blue >= 192){ //blue bits
				val64 += 3;
			}
			else if (blue >= 128){
				val64 += 2;
			}
			else if (blue >= 64){
				val64 += 1;
			}

			query64bin[val64] += 1;

		}/*end of for j*/
	}/*end of for i*/
}

void calculate64(Mat image, int **rgb64bin, int imgNumber){
	int i, j;
	int val64;
	Vec3b color;
	uchar blue;
	uchar green;
	uchar red;
	int rows = image.rows;
	int cols = image.cols;

	for (int i = 0; i < rows; i++){
		for (int j = 0; j < cols; j++){
			//system("pause");
			color = image.at<Vec3b>(i, j);
			blue = color.val[0];
			green = color.val[1];
			red = color.val[2];
			//printf("r:%d g:%d b:%d   ", red, green, blue);
			val64 = 0;
			if (red >= 192){ //red bits
				val64 += 48;
			}
			else if (red >= 128){
				val64 += 32;
			}
			else if (red >= 64){
				val64 += 16;
			}

			if (green >= 192){ //green bits
				val64 += 12;
			}
			else if (green >= 128){
				val64 += 8;
			}
			else if (green >= 64){
				val64 += 4;
			}

			if (blue >= 192){ //blue bits
				val64 += 3;
			}
			else if (blue >= 128){
				val64 += 2;
			}
			else if (blue >= 64){
				val64 += 1;
			}

			rgb64bin[imgNumber][val64] += 1;
			//printf("\nval64: %d   rgb64bin: %d\n\n",val64, rgb64bin[imgNumber][val64]);
		}/*end of for j*/
	}/*end of for i*/
}

void calculateDistance(int query[], int **database, float distanceArray[], int n, int m){
	int i, j, k;
	long sum;

	for (i = 0; i < n; i++){
		sum = 0;
		for (j = 0; j < m; j++){
			sum += (query[j] - database[i][j]) * (query[j] - database[i][j]);
		}
		distanceArray[i] = sqrt(sum);
	}
}

void sortCalculatedArray(int sampleCount,float distanceArray[], int sortedArray[]){
	int min = 0;
	int i = 0;
	int j;
	while (i < sampleCount){
		j = 0;
		while ((distanceArray[min] == -1) && (distanceArray[min] != 0)){
			if (distanceArray[j] > 0){
				min = j;
			}
			j++;
		}
		for (j = 0; j < sampleCount; j++){
			if ((distanceArray[min]>distanceArray[j]) && (distanceArray[j] != (-1))){
				min = j;
			}
		}
		distanceArray[min] = -1;
		sortedArray[i] = min;
		i++;
	}
}

int getIndexOf58(int number){
	int array58[58] = { 0, 1, 2, 3, 4, 6, 7, 8, 12, 14, 15, 16, 24, 28, 30, 31, 32, 48, 56, 60, 62,
		63, 64, 96, 112, 120, 124, 126, 127, 128, 129, 131,	135, 143, 159, 191, 192, 193, 195, 199,
		207, 223, 224, 225, 227, 231, 239, 240, 241, 243, 247, 248, 249, 251, 252, 253, 254, 255 };
	int i;
	for (i = 0; i < 58; i++){
		if (number == array58[i]){
			return i;
		}
	}
	return 58;
}