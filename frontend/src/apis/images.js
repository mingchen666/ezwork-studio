import request from "@/utils/request";

// 保存绘图图片
export function saveImageService(data) {
  return request({
    url: "/images/add", 
    method: "post",
    data,
  });
}

// 获取图片列表最多20个
export function getImagesListService(params = {}) {
  return request({
    url: "/images/list", 
    method: "get",
    params,  // 支持查询参数，如 simple=true
  });
}

// 获取图片详情
export function getImageDetailService(imageId) {
  return request({
    url: `/images/${imageId}`,
    method: "get",
  });
}

// 更新图片信息
export function updateImageService(imageId, data) {
  return request({
    url: `/images/${imageId}`,
    method: "put",
    data,
  });
}

// 删除图片
export function deleteImageService(imageId) {
  return request({
    url: `/images/${imageId}`,
    method: "delete",
  });
}

// URL转Base64
export function urlToBase64Service(imageUrl) {
  return request({
    url: "/images/url-to-base64",
    method: "post",
    data: {
      image_url: imageUrl
    }
  });
}
