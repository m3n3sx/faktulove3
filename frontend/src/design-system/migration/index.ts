/**
 * Design System Migration Utilities
 * 
 * This module provides utilities for migrating existing FaktuLove components
 * to use the new design system while maintaining backward compatibility.
 */

export { CompatibilityLayer } from './CompatibilityLayer';
export { ComponentMigrator } from './ComponentMigrator';
export { StyleMigrator } from './StyleMigrator';
export { ThemeMigrator } from './ThemeMigrator';
export { migrationConfig } from './config';
export type { MigrationOptions, ComponentMapping, StyleMapping } from './types';