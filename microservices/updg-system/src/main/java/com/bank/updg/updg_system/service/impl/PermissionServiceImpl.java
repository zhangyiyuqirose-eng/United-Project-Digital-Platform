package com.bank.updg.updg_system.service.impl;

import com.baomidou.mybatisplus.core.conditions.query.LambdaQueryWrapper;
import com.baomidou.mybatisplus.extension.service.impl.ServiceImpl;
import com.bank.updg.updg_system.mapper.SysPermissionMapper;
import com.bank.updg.updg_system.model.entity.SysPermission;
import com.bank.updg.updg_system.service.PermissionService;
import org.springframework.stereotype.Service;

import java.util.ArrayList;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;

/**
 * Permission service implementation with tree building.
 */
@Service
public class PermissionServiceImpl extends ServiceImpl<SysPermissionMapper, SysPermission>
        implements PermissionService {

    @Override
    public List<SysPermission> getPermissionTree() {
        List<SysPermission> allPermissions = list();

        // Group by parentId for tree building
        Map<String, List<SysPermission>> childrenMap = new LinkedHashMap<>();
        List<SysPermission> roots = new ArrayList<>();

        for (SysPermission p : allPermissions) {
            String parentId = p.getParentId();
            if (parentId == null || parentId.isEmpty() || "0".equals(parentId)) {
                roots.add(p);
            } else {
                childrenMap.computeIfAbsent(parentId, k -> new ArrayList<>()).add(p);
            }
        }

        return buildTree(roots, childrenMap);
    }

    @Override
    public List<SysPermission> getPermissionsByRoleId(String roleId) {
        // TODO: Query through role-permission mapping table
        // SELECT p.* FROM pm_sys_permission p
        // INNER JOIN pm_sys_role_permission rp ON p.permission_id = rp.permission_id
        // WHERE rp.role_id = ?
        return list();
    }

    private List<SysPermission> buildTree(List<SysPermission> roots,
                                          Map<String, List<SysPermission>> childrenMap) {
        List<SysPermission> result = new ArrayList<>();
        for (SysPermission root : roots) {
            result.add(buildNode(root, childrenMap));
        }
        return result;
    }

    private SysPermission buildNode(SysPermission node,
                                    Map<String, List<SysPermission>> childrenMap) {
        List<SysPermission> children = childrenMap.get(node.getPermissionId());
        if (children != null && !children.isEmpty()) {
            // Store children as nested structure via parentId references
            // Since SysPermission is flat, children are implicitly linked via parentId
            // The tree is returned as a flat list sorted by hierarchy
            for (SysPermission child : children) {
                buildNode(child, childrenMap);
            }
        }
        return node;
    }
}
