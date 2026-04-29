package com.bank.updg.updg_system.controller;

import com.bank.updg.common.model.ApiResponse;
import com.bank.updg.updg_system.model.entity.SysDict;
import com.bank.updg.updg_system.service.SysDictService;
import lombok.RequiredArgsConstructor;
import org.springframework.web.bind.annotation.*;

import java.util.List;
import java.util.Map;

@RestController
@RequestMapping("/api/system/dict")
@RequiredArgsConstructor
public class SysDictController {

    private final SysDictService dictService;

    @GetMapping
    public ApiResponse<List<SysDict>> list() {
        return ApiResponse.success(dictService.list());
    }

    @GetMapping("/{code}")
    public ApiResponse<Map<String, Object>> getByCode(@PathVariable String code) {
        return ApiResponse.success(dictService.getDictByCode(code));
    }

    @PostMapping
    public ApiResponse<Void> create(@RequestBody SysDict dict) {
        dictService.save(dict);
        return ApiResponse.success();
    }

    @PutMapping("/{id}")
    public ApiResponse<Void> update(@PathVariable String id, @RequestBody SysDict dict) {
        dict.setDictId(id);
        dictService.updateById(dict);
        return ApiResponse.success();
    }

    @DeleteMapping("/{id}")
    public ApiResponse<Void> delete(@PathVariable String id) {
        dictService.removeById(id);
        return ApiResponse.success();
    }
}
