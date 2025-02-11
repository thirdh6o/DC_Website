Page({
  data: {
    photo: '',
    processedImage: '',
    isProcessing: false,
  },

  chooseImage() {
    wx.chooseImage({
      count: 1,
      sourceType: ['album', 'camera'],
      success: (res) => {
        this.setData({
          photo: res.tempFilePaths[0],
          processedImage: ''  // 清空处理后的图片
        });
      }
    });
  },

  uploadImage() {
    if (!this.data.photo) {
      wx.showToast({
        title: '请先选择图片',
        icon: 'none'
      });
      return;
    }

    this.setData({ isProcessing: true });

    wx.uploadFile({
      url: 'https://你的服务器地址/api/wx_upload_photo.php',  // 替换为你的服务器地址
      filePath: this.data.photo,
      name: 'photo',
      success: (res) => {
        const data = JSON.parse(res.data);
        if (data.success) {
          this.setData({
            processedImage: data.processedImage  // 设置处理后的图片
          });
          wx.showToast({
            title: '上传成功',
            icon: 'success'
          });
        } else {
          wx.showToast({
            title: data.error || '上传失败',
            icon: 'none'
          });
        }
      },
      fail: (error) => {
        wx.showToast({
          title: '上传失败，请重试',
          icon: 'none'
        });
      },
      complete: () => {
        this.setData({ isProcessing: false });
      }
    });
  }
}); 