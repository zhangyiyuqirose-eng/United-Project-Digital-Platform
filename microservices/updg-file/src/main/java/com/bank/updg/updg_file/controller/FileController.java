package com.bank.updg.updg_file.controller;

import com.baomidou.mybatisplus.extension.plugins.pagination.Page;
import com.bank.updg.common.model.ApiResponse;
import com.bank.updg.updg_file.model.entity.FileInfo;
import com.bank.updg.updg_file.service.ArchiveService;
import com.bank.updg.updg_file.service.FileService;
import jakarta.servlet.http.HttpServletResponse;
import lombok.RequiredArgsConstructor;
import org.springframework.http.MediaType;
import org.springframework.web.bind.annotation.*;
import org.springframework.web.multipart.MultipartFile;

import java.io.InputStream;
import java.io.OutputStream;
import java.net.URLEncoder;
import java.nio.charset.StandardCharsets;

@RestController
@RequestMapping("/api/file")
@RequiredArgsConstructor
public class FileController {

    private final FileService fileService;
    private final ArchiveService archiveService;

    @PostMapping("/upload")
    public ApiResponse<FileInfo> upload(
            @RequestParam("file") MultipartFile file,
            @RequestParam String projectId,
            @RequestParam(required = false) String category) {
        try (InputStream input = file.getInputStream()) {
            // TODO: resolve uploadedBy from security context
            String uploadedBy = "system";
            FileInfo info = fileService.uploadFile(
                    input,
                    file.getOriginalFilename(),
                    file.getContentType(),
                    file.getSize(),
                    uploadedBy,
                    projectId,
                    category);
            return ApiResponse.success(info);
        } catch (Exception e) {
            return ApiResponse.error(com.bank.updg.common.model.enums.ErrorCodeEnum.SYSTEM_ERROR, e.getMessage());
        }
    }

    @GetMapping("/{fileId}")
    public ApiResponse<FileInfo> getFileInfo(@PathVariable String fileId) {
        return ApiResponse.success(fileService.getFileInfo(fileId));
    }

    @GetMapping("/{fileId}/download")
    public void downloadFile(@PathVariable String fileId, HttpServletResponse response) {
        FileInfo info = fileService.getFileInfo(fileId);
        try (InputStream input = fileService.downloadFile(fileId);
             OutputStream output = response.getOutputStream()) {

            response.setContentType(MediaType.APPLICATION_OCTET_STREAM_VALUE);
            String encodedName = URLEncoder.encode(info.getOriginalName(), StandardCharsets.UTF_8).replace("+", "%20");
            response.setHeader("Content-Disposition", "attachment; filename=\"" + encodedName + "\"");

            byte[] buffer = new byte[8192];
            int bytesRead;
            while ((bytesRead = input.read(buffer)) != -1) {
                output.write(buffer, 0, bytesRead);
            }
            output.flush();

        } catch (Exception e) {
            throw new RuntimeException("Failed to download file", e);
        }
    }

    @GetMapping("/{fileId}/preview")
    public ApiResponse<String> previewUrl(@PathVariable String fileId) {
        return ApiResponse.success(fileService.previewUrl(fileId));
    }

    @GetMapping("/list")
    public ApiResponse<Page<FileInfo>> listFiles(
            @RequestParam(required = false) String projectId,
            @RequestParam(required = false) String category,
            @RequestParam(defaultValue = "1") int page,
            @RequestParam(defaultValue = "10") int size) {
        return ApiResponse.success(fileService.listFiles(projectId, category, page, size));
    }

    @DeleteMapping("/{fileId}")
    public ApiResponse<Void> deleteFile(@PathVariable String fileId) {
        // TODO: resolve userId from security context
        String userId = "system";
        fileService.deleteFile(fileId, userId);
        return ApiResponse.success();
    }

    /**
     * F-404: Archive all documents for a project.
     */
    @PostMapping("/archive/{projectId}")
    public ApiResponse<Void> archiveProject(@PathVariable String projectId) {
        archiveService.archiveProjectDocuments(projectId);
        return ApiResponse.success();
    }
}
