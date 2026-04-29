package com.bank.updg.updg_file.service;

import com.baomidou.mybatisplus.extension.plugins.pagination.Page;
import com.bank.updg.updg_file.model.entity.FileInfo;

import java.io.InputStream;

public interface FileService {

    FileInfo uploadFile(InputStream input, String fileName, String contentType, Long size,
                        String uploadedBy, String projectId, String category);

    InputStream downloadFile(String fileId);

    FileInfo getFileInfo(String fileId);

    Page<FileInfo> listFiles(String projectId, String category, int page, int size);

    void deleteFile(String fileId, String userId);

    String previewUrl(String fileId);
}
